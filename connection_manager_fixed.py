#!/usr/bin/env python3
"""
Fixed Connection Manager for Deriv API
Solves the WebSocket concurrency issue by using a single message listener
with request/response queues to handle multiple concurrent operations.
"""

import asyncio
import logging
import json
import time
import uuid
from typing import Dict, Any, Optional, Callable
from collections import defaultdict, deque
import websockets
from datetime import datetime

logger = logging.getLogger(__name__)

class DerivConnectionManager:
    """
    Fixed connection manager that solves the WebSocket concurrency issue.
    Uses a single message listener with request/response queues.
    """
    
    def __init__(self, app_id: str, api_token: str = None):
        self.app_id = app_id
        self.api_token = api_token
        self.ws = None
        self.is_connected = False
        self.is_connecting = False
        
        # Single message listener to prevent concurrency issues
        self._message_listener_task = None
        
        # Request/response handling
        self._pending_requests = {}  # request_id -> future
        self._request_lock = asyncio.Lock()
        
        # Subscription handling
        self._subscriptions = {}  # symbol -> subscription_id
        self._subscription_callbacks = {}  # symbol -> callback
        self._price_data = defaultdict(lambda: deque(maxlen=1000))
        self._last_prices = {}
        
        # Connection health
        self._last_ping = time.time()
        self._ping_task = None
        
    async def connect(self):
        """Connect to Deriv WebSocket API"""
        if self.is_connected or self.is_connecting:
            return
            
        self.is_connecting = True
        
        try:
            # WebSocket URL for Deriv API
            ws_url = "wss://ws.derivws.com/websockets/v3"
            if self.api_token:
                ws_url += f"?app_id={self.app_id}"
            else:
                ws_url += f"?app_id={self.app_id}"
                
            logger.info(f"🔗 Connecting to Deriv WebSocket...")
            self.ws = await websockets.connect(ws_url)
            
            # Mark as connected first
            self.is_connected = True
            self.is_connecting = False
            
            # Start the single message listener
            self._message_listener_task = asyncio.create_task(self._message_listener())
            
            # Start ping task to keep connection alive
            self._ping_task = asyncio.create_task(self._ping_loop())
            
            # Give the message listener a moment to start
            await asyncio.sleep(0.1)
            
            # Always try to authorize (handles both token and demo accounts)
            await self._authorize()
            
            logger.info("✅ Connected to Deriv WebSocket")
            
        except Exception as e:
            self.is_connecting = False
            self.is_connected = False
            logger.error(f"❌ Failed to connect: {e}")
            raise
            
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if not self.is_connected:
            return
            
        self.is_connected = False
        
        # Cancel tasks
        if self._message_listener_task and not self._message_listener_task.done():
            self._message_listener_task.cancel()
            
        if self._ping_task and not self._ping_task.done():
            self._ping_task.cancel()
            
        # Close WebSocket
        if self.ws:
            await self.ws.close()
            self.ws = None
            
        # Clear pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()
        
        logger.info("🔌 Disconnected from Deriv WebSocket")
        
    async def _authorize(self):
        """Authorize the connection with API token or create demo account"""
        if self.api_token:
            # Use a simple numeric ID instead of UUID
            import random
            req_id = random.randint(1000, 9999)
            
            auth_request = {
                "authorize": self.api_token,
                "req_id": req_id
            }
            
            response = await self._send_request(auth_request)
            
            if "error" in response:
                raise Exception(f"Authorization failed: {response['error']['message']}")
                
            logger.info("✅ Authorized with Deriv API")
        else:
            # For demo accounts, we cannot create virtual accounts without proper setup
            # The bot should either:
            # 1. Use a pre-configured demo token
            # 2. Show demo-like functionality without real account data
            # 3. Guide users to connect their own accounts
            logger.info("ℹ️ No API token provided - limited to public endpoints only")
            logger.info("💡 Users should connect their own account with /connect command for full functionality")
        
    async def _message_listener(self):
        """
        Single message listener that handles all incoming WebSocket messages.
        This prevents the 'recv while another coroutine is already running recv' error.
        """
        try:
            while self.is_connected and self.ws:
                try:
                    message = await self.ws.recv()
                    data = json.loads(message)
                    
                    # Handle different message types
                    if "req_id" in data:
                        # This is a response to a request
                        req_id = data["req_id"]
                        if req_id in self._pending_requests:
                            future = self._pending_requests.pop(req_id)
                            if not future.done():
                                future.set_result(data)
                                
                    elif "subscription" in data:
                        # This is a subscription update (live data)
                        await self._handle_subscription_message(data)
                        
                    else:
                        logger.debug(f"Received unhandled message: {data}")
                        
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message: {e}")
                except Exception as e:
                    logger.error(f"Error in message listener: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Message listener cancelled")
        except Exception as e:
            logger.error(f"Message listener error: {e}")
        finally:
            self.is_connected = False
            
    async def _handle_subscription_message(self, data):
        """Handle subscription messages (live price updates)"""
        try:
            if "tick" in data:
                tick_data = data["tick"]
                symbol = tick_data.get("symbol", "")
                
                # Update price data
                self._last_prices[symbol] = tick_data
                self._price_data[symbol].append({
                    "price": tick_data.get("quote", 0),
                    "time": tick_data.get("epoch", time.time()),
                    "symbol": symbol
                })
                
                # Call subscription callback if registered
                if symbol in self._subscription_callbacks:
                    callback = self._subscription_callbacks[symbol]
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(tick_data)
                        else:
                            callback(tick_data)
                    except Exception as e:
                        logger.error(f"Error in subscription callback for {symbol}: {e}")
                        
        except Exception as e:
            logger.error(f"Error handling subscription message: {e}")
            
    async def _send_request(self, request_data):
        """
        Send a request and wait for response using the request/response queue system.
        This ensures only one coroutine is reading from the WebSocket.
        """
        if not self.is_connected or not self.ws:
            raise Exception("Not connected to WebSocket")
            
        # Generate unique request ID if not present
        if "req_id" not in request_data:
            import random
            request_data["req_id"] = random.randint(1000, 9999)
            
        req_id = request_data["req_id"]
        
        # Create future for response
        future = asyncio.Future()
        
        async with self._request_lock:
            self._pending_requests[req_id] = future
            
            # Send request
            try:
                await self.ws.send(json.dumps(request_data))
                logger.debug(f"Sent request: {request_data}")
            except Exception as e:
                # Clean up on send failure
                self._pending_requests.pop(req_id, None)
                raise e
                
        # Wait for response (with timeout)
        try:
            response = await asyncio.wait_for(future, timeout=30.0)
            return response
        except asyncio.TimeoutError:
            # Clean up on timeout
            self._pending_requests.pop(req_id, None)
            raise Exception("Request timeout")
            
    async def _ping_loop(self):
        """Send periodic pings to keep connection alive"""
        try:
            while self.is_connected:
                await asyncio.sleep(30)  # Ping every 30 seconds
                if self.is_connected and self.ws:
                    try:
                        import random
                        ping_request = {
                            "ping": 1,
                            "req_id": random.randint(1000, 9999)
                        }
                        await self._send_request(ping_request)
                        self._last_ping = time.time()
                    except Exception as e:
                        logger.warning(f"Ping failed: {e}")
        except asyncio.CancelledError:
            pass
            
    # API Methods
    async def get_balance(self):
        """Get account balance"""
        request = {
            "balance": 1
        }
        return await self._send_request(request)
        
    async def get_active_symbols(self):
        """Get active trading symbols"""
        request = {
            "active_symbols": "brief",
            "product_type": "basic"
        }
        return await self._send_request(request)
        
    async def get_ticks(self, symbol: str):
        """Get current tick for a symbol"""
        request = {
            "ticks": symbol
        }
        return await self._send_request(request)
        
    async def subscribe_ticks(self, symbol: str, callback: Callable = None):
        """Subscribe to live tick data for a symbol"""
        request = {
            "ticks": symbol,
            "subscribe": 1
        }
        
        response = await self._send_request(request)
        
        if "error" not in response and "subscription" in response:
            subscription_id = response["subscription"]["id"]
            self._subscriptions[symbol] = subscription_id
            
            if callback:
                self._subscription_callbacks[symbol] = callback
                
        return response
        
    async def unsubscribe_ticks(self, symbol: str):
        """Unsubscribe from tick data"""
        if symbol not in self._subscriptions:
            return
            
        subscription_id = self._subscriptions[symbol]
        request = {
            "forget": subscription_id
        }
        
        response = await self._send_request(request)
        
        # Clean up
        self._subscriptions.pop(symbol, None)
        self._subscription_callbacks.pop(symbol, None)
        
        return response
        
    def get_latest_price(self, symbol: str):
        """Get the latest price for a symbol"""
        return self._last_prices.get(symbol)
        
    def get_price_history(self, symbol: str, limit: int = 100):
        """Get price history for a symbol"""
        return list(self._price_data[symbol])[-limit:] if symbol in self._price_data else []


# Global connection manager instance
_connection_manager = None

def get_connection_manager(app_id: str = None, api_token: str = None):
    """
    Get or create the global connection manager instance.
    This ensures we have a single connection manager across the application.
    """
    global _connection_manager
    
    if _connection_manager is None:
        if not app_id:
            raise ValueError("app_id is required for first connection manager creation")
        _connection_manager = DerivConnectionManager(app_id, api_token)
    
    return _connection_manager


class DerivAPI:
    """
    Deriv API client that uses the fixed connection manager.
    This replaces the old DerivAPI class that had concurrency issues.
    """
    
    def __init__(self, app_id: str, api_token: str = None):
        self.app_id = app_id
        self.api_token = api_token
        self._connection_manager = None
        
    async def connect(self):
        """Connect to Deriv API"""
        # If we have a token, create a new connection manager with the token
        # If no token, use the global connection manager
        if self.api_token:
            # User has their own token, create dedicated connection
            self._connection_manager = DerivConnectionManager(self.app_id, self.api_token)
        else:
            # No token, use global connection manager
            global _connection_manager
            if _connection_manager is None:
                _connection_manager = DerivConnectionManager(self.app_id)
            self._connection_manager = _connection_manager
        
        # Connect if not already connected
        if not self._connection_manager.is_connected:
            await self._connection_manager.connect()
        
    async def disconnect(self):
        """Disconnect from Deriv API"""
        if self._connection_manager:
            await self._connection_manager.disconnect()
            self._connection_manager = None
            
    async def get_balance(self):
        """Get account balance"""
        if not self._connection_manager:
            await self.connect()
        return await self._connection_manager.get_balance()
        
    async def get_active_symbols(self):
        """Get active trading symbols"""
        if not self._connection_manager:
            await self.connect()
        return await self._connection_manager.get_active_symbols()
        
    async def get_ticks(self, symbol: str):
        """Get current tick for a symbol"""
        if not self._connection_manager:
            await self.connect()
        return await self._connection_manager.get_ticks(symbol)
        
    async def subscribe_ticks(self, symbol: str, callback: Callable = None):
        """Subscribe to live tick data"""
        if not self._connection_manager:
            await self.connect()
        return await self._connection_manager.subscribe_ticks(symbol, callback)
        
    async def unsubscribe_ticks(self, symbol: str):
        """Unsubscribe from tick data"""
        if not self._connection_manager:
            return
        return await self._connection_manager.unsubscribe_ticks(symbol)
        
    # Backward compatibility methods
    async def subscribe_to_live_prices(self, symbol: str, callback: Callable = None):
        """Subscribe to live price updates (backward compatibility)"""
        return await self.subscribe_ticks(symbol, callback)
        
    async def unsubscribe_from_live_prices(self, symbol: str):
        """Unsubscribe from live price updates (backward compatibility)"""
        return await self.unsubscribe_ticks(symbol)
        
    def get_latest_price(self, symbol: str):
        """Get the latest cached price for a symbol"""
        if not self._connection_manager:
            return None
        return self._connection_manager.get_latest_price(symbol)
        
    def get_price_history(self, symbol: str, limit: int = 100):
        """Get price history for a symbol"""
        if not self._connection_manager:
            return []
        return self._connection_manager.get_price_history(symbol, limit)
        
    async def buy_contract(self, contract_type: str, symbol: str, amount: float, duration: int, duration_unit: str = "t"):
        """Buy a contract"""
        if not self._connection_manager:
            await self.connect()
        
        request = {
            "buy": 1,
            "price": amount,
            "parameters": {
                "contract_type": contract_type,
                "symbol": symbol,
                "duration": duration,
                "duration_unit": duration_unit,
                "amount": amount
            }
        }
        return await self._connection_manager._send_request(request)
        
    async def get_proposal(self, contract_type: str, symbol: str, amount: float, duration: int, duration_unit: str = "t"):
        """Get proposal for a contract"""
        if not self._connection_manager:
            await self.connect()
            
        request = {
            "proposal": 1,
            "contract_type": contract_type,
            "symbol": symbol,
            "amount": amount,
            "duration": duration,
            "duration_unit": duration_unit
        }
        return await self._connection_manager._send_request(request)
        
    async def get_portfolio(self):
        """Get portfolio/open positions"""
        if not self._connection_manager:
            await self.connect()
            
        request = {"portfolio": 1}
        return await self._connection_manager._send_request(request)
        
    async def get_profit_table(self, symbol: str = None, contract_type: str = "CALL"):
        """Get profit table"""
        if not self._connection_manager:
            await self.connect()
            
        request = {"profit_table": 1}
        if symbol:
            request["symbol"] = symbol
        if contract_type:
            request["contract_type"] = contract_type
            
        return await self._connection_manager._send_request(request)
    
    async def send_request(self, request_data):
        """Send a custom request to the Deriv API"""
        if not self._connection_manager:
            await self.connect()
        return await self._connection_manager._send_request(request_data)
    
    @property
    def is_connected(self):
        """Check if connected to Deriv API"""
        return self._connection_manager and self._connection_manager.is_connected
    
    async def authorize(self):
        """Authorize the connection - returns True if successful"""
        if not self._connection_manager:
            await self.connect()
        
        # If no token, consider it authorized (demo mode)
        if not self.api_token:
            return True
            
        try:
            # The authorization is handled during connection
            # If we're connected and have a token, we're authorized
            return self.is_connected
        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            return False
