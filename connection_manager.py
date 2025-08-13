#!/usr/bin/env python3
"""
Connection Manager for maintaining persistent WebSocket connections to Deriv API
Handles live price streams, automatic reconnection, and connection pooling
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional, Callable, Set
from collections import defaultdict, deque
import websockets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ConnectionPool:
    """Manages multiple WebSocket connections to Deriv API"""
    
    def __init__(self, app_id: str, max_connections: int = 10):
        self.app_id = app_id
        self.max_connections = max_connections
        self.connections: Dict[str, 'ManagedConnection'] = {}
        self.active_subscriptions: Dict[str, Set[str]] = defaultdict(set)  # connection_id -> set of symbols
        self.subscription_callbacks: Dict[str, Callable] = {}  # symbol -> callback
        self.price_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.last_prices: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        
    async def start(self):
        """Start the connection pool"""
        self.is_running = True
        logger.info("🔗 Connection pool started")
        
    async def stop(self):
        """Stop all connections"""
        self.is_running = False
        for connection in self.connections.values():
            await connection.disconnect()
        self.connections.clear()
        self.active_subscriptions.clear()
        logger.info("🔌 Connection pool stopped")
        
    async def get_connection(self, api_token: str = None) -> 'ManagedConnection':
        """Get or create a connection for an API token"""
        connection_id = api_token or "default"
        
        if connection_id not in self.connections:
            if len(self.connections) >= self.max_connections:
                # Remove least recently used connection
                oldest_conn_id = min(self.connections.keys(), 
                                   key=lambda x: self.connections[x].last_used)
                await self.connections[oldest_conn_id].disconnect()
                del self.connections[oldest_conn_id]
                
            # Create new connection
            self.connections[connection_id] = ManagedConnection(
                self.app_id, api_token, connection_id, self
            )
            
        connection = self.connections[connection_id]
        
        # Ensure connection is active
        if not connection.is_connected:
            await connection.connect()
            
        return connection
        
    async def subscribe_to_ticks(self, symbol: str, callback: Callable = None, api_token: str = None):
        """Subscribe to live tick data for a symbol"""
        connection = await self.get_connection(api_token)
        
        # Store callback if provided
        if callback:
            self.subscription_callbacks[symbol] = callback
            
        # Subscribe to ticks
        await connection.subscribe_ticks(symbol)
        
    async def unsubscribe_from_ticks(self, symbol: str, api_token: str = None):
        """Unsubscribe from tick data"""
        connection = await self.get_connection(api_token)
        await connection.unsubscribe_ticks(symbol)
        
        # Remove callback
        if symbol in self.subscription_callbacks:
            del self.subscription_callbacks[symbol]
            
    def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get the latest price for a symbol"""
        return self.last_prices.get(symbol)
        
    def get_price_history(self, symbol: str, limit: int = 100) -> list:
        """Get price history for a symbol"""
        return list(self.price_data[symbol])[-limit:] if symbol in self.price_data else []
        
    def _update_price_data(self, symbol: str, tick_data: Dict[str, Any]):
        """Update internal price data storage"""
        self.last_prices[symbol] = tick_data
        self.price_data[symbol].append(tick_data)
        
        # Call registered callback if exists
        if symbol in self.subscription_callbacks:
            try:
                asyncio.create_task(self.subscription_callbacks[symbol](symbol, tick_data))
            except Exception as e:
                logger.error(f"Error calling price callback for {symbol}: {e}")

class ManagedConnection:
    """A managed WebSocket connection with automatic reconnection"""
    
    def __init__(self, app_id: str, api_token: str, connection_id: str, pool: ConnectionPool):
        self.app_id = app_id
        self.api_token = api_token
        self.connection_id = connection_id
        self.pool = pool
        self.websocket = None
        self.is_connected = False
        self.is_authorized = False
        self.last_used = time.time()
        self.request_id = 0
        self.subscriptions: Set[str] = set()
        self.reconnect_delay = 5  # seconds
        self.max_reconnect_attempts = 5
        self.message_handlers = {
            'tick': self._handle_tick,
            'balance': self._handle_balance,
            'authorize': self._handle_authorize,
            'error': self._handle_error
        }
        
    async def connect(self) -> bool:
        """Connect to Deriv WebSocket API"""
        for attempt in range(self.max_reconnect_attempts):
            try:
                uri = f"wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}"
                logger.info(f"🔗 Connecting to Deriv API (attempt {attempt + 1}/{self.max_reconnect_attempts})")
                
                self.websocket = await asyncio.wait_for(
                    websockets.connect(
                        uri,
                        ping_interval=30,
                        ping_timeout=20,
                        close_timeout=10,
                        max_size=10**7,
                        read_limit=10**7
                    ),
                    timeout=30
                )
                
                self.is_connected = True
                self.last_used = time.time()
                logger.info(f"✅ Connected to Deriv API")
                
                # Start message listener
                asyncio.create_task(self._message_listener())
                
                # Authorize if token provided
                if self.api_token:
                    await self._authorize()
                    
                return True
                
            except Exception as e:
                logger.error(f"❌ Connection failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_reconnect_attempts - 1:
                    await asyncio.sleep(self.reconnect_delay * (attempt + 1))
                    
        return False
        
    async def disconnect(self):
        """Disconnect from API"""
        self.is_connected = False
        self.is_authorized = False
        if self.websocket:
            await self.websocket.close()
            logger.info(f"🔌 Disconnected connection {self.connection_id}")
            
    async def _authorize(self) -> bool:
        """Authorize with API token"""
        if not self.api_token or not self.is_connected:
            return False
            
        try:
            request = {
                "authorize": self.api_token,
                "req_id": self._get_request_id()
            }
            
            await self.websocket.send(json.dumps(request))
            # Authorization response will be handled by _handle_authorize
            return True
            
        except Exception as e:
            logger.error(f"❌ Authorization failed: {e}")
            return False
            
    async def _message_listener(self):
        """Listen for incoming WebSocket messages"""
        try:
            while self.is_connected and self.websocket:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=60)
                    data = json.loads(message)
                    await self._handle_message(data)
                    
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    if self.is_connected and self.websocket:
                        await self.websocket.ping()
                        
                except websockets.exceptions.ConnectionClosed:
                    logger.warning(f"⚠️ Connection {self.connection_id} closed by server")
                    break
                    
                except Exception as e:
                    logger.error(f"❌ Message listener error: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Message listener crashed: {e}")
            
        # Attempt reconnection if we're supposed to be connected
        if self.pool.is_running and self.connection_id in self.pool.connections:
            logger.info(f"🔄 Attempting to reconnect {self.connection_id}")
            await asyncio.sleep(self.reconnect_delay)
            await self.connect()
            
            # Re-subscribe to previous subscriptions
            for symbol in self.subscriptions.copy():
                await self.subscribe_ticks(symbol)
                
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        self.last_used = time.time()
        
        # Determine message type
        msg_type = None
        if 'tick' in data:
            msg_type = 'tick'
        elif 'balance' in data:
            msg_type = 'balance'
        elif 'authorize' in data:
            msg_type = 'authorize'
        elif 'error' in data:
            msg_type = 'error'
            
        # Call appropriate handler
        if msg_type and msg_type in self.message_handlers:
            await self.message_handlers[msg_type](data)
        else:
            logger.debug(f"📨 Unhandled message type: {data}")
            
    async def _handle_tick(self, data: Dict[str, Any]):
        """Handle tick data"""
        tick = data.get('tick', {})
        symbol = tick.get('symbol')
        
        if symbol:
            # Update pool price data
            self.pool._update_price_data(symbol, tick)
            logger.debug(f"📈 {symbol}: {tick.get('quote', 'N/A')}")
            
    async def _handle_balance(self, data: Dict[str, Any]):
        """Handle balance updates"""
        balance = data.get('balance', {})
        logger.debug(f"💰 Balance update: {balance.get('balance', 'N/A')} {balance.get('currency', 'USD')}")
        
    async def _handle_authorize(self, data: Dict[str, Any]):
        """Handle authorization response"""
        if 'error' in data:
            error_msg = data['error'].get('message', 'Unknown error')
            logger.error(f"❌ Authorization failed: {error_msg}")
            self.is_authorized = False
        else:
            logger.info(f"✅ Authorization successful for {self.connection_id}")
            self.is_authorized = True
            
    async def _handle_error(self, data: Dict[str, Any]):
        """Handle error messages"""
        error = data.get('error', {})
        error_msg = error.get('message', 'Unknown error')
        logger.error(f"❌ API Error: {error_msg}")
        
    async def subscribe_ticks(self, symbol: str):
        """Subscribe to tick data for a symbol"""
        if not self.is_connected:
            await self.connect()
            
        try:
            request = {
                "ticks": symbol,
                "subscribe": 1,
                "req_id": self._get_request_id()
            }
            
            await self.websocket.send(json.dumps(request))
            self.subscriptions.add(symbol)
            logger.info(f"📊 Subscribed to {symbol} ticks")
            
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to {symbol}: {e}")
            
    async def unsubscribe_ticks(self, symbol: str):
        """Unsubscribe from tick data"""
        if not self.is_connected or symbol not in self.subscriptions:
            return
            
        try:
            request = {
                "forget_all": "ticks"
            }
            
            await self.websocket.send(json.dumps(request))
            self.subscriptions.discard(symbol)
            logger.info(f"🔇 Unsubscribed from {symbol} ticks")
            
        except Exception as e:
            logger.error(f"❌ Failed to unsubscribe from {symbol}: {e}")
            
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request and wait for response"""
        if not self.is_connected:
            await self.connect()
            
        try:
            request["req_id"] = self._get_request_id()
            await self.websocket.send(json.dumps(request))
            
            # For subscriptions, don't wait for response
            if "subscribe" in request:
                return {"status": "subscribed"}
                
            # Wait for response (simplified for now)
            response = await asyncio.wait_for(self.websocket.recv(), timeout=30)
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return {"error": {"message": str(e)}}
            
    def _get_request_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id

class ConnectionManager:
    """High-level interface to the connection pool for easy usage"""
    
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.pool = None
        
    async def initialize(self):
        """Initialize the connection pool"""
        if not self.pool:
            self.pool = ConnectionPool(self.app_id)
            await self.pool.start()
        return self.pool
        
    async def send_request(self, request: Dict[str, Any], api_token: str = None) -> Dict[str, Any]:
        """Send a request through the connection pool"""
        if not self.pool:
            await self.initialize()
        
        connection = await self.pool.get_connection(api_token)
        return await connection.send_request(request)
        
    async def subscribe_to_symbol(self, symbol: str, callback: Callable):
        """Subscribe to live prices for a symbol"""
        if not self.pool:
            await self.initialize()
        
        await self.pool.subscribe_to_live_prices(symbol, callback)
        
    async def unsubscribe_from_symbol(self, symbol: str):
        """Unsubscribe from live prices for a symbol"""
        if not self.pool:
            await self.initialize()
            
        await self.pool.unsubscribe_from_live_prices(symbol)
        
    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """Get the latest price for a symbol"""
        if not self.pool:
            await self.initialize()
            
        return self.pool.get_latest_price(symbol)
        
    async def get_price_history(self, symbol: str, count: int = 10) -> list:
        """Get price history for a symbol"""
        if not self.pool:
            await self.initialize()
            
        return self.pool.get_price_history(symbol, count)
        
    @property
    def connections(self):
        """Get the connections dict for status checking"""
        if self.pool:
            return self.pool.connections
        return {}
        
    async def close_all_connections(self):
        """Close all connections"""
        if self.pool:
            await self.pool.stop()
            self.pool = None

# Global connection pool instance
_connection_pool: Optional[ConnectionPool] = None

def get_connection_pool(app_id: str = None) -> ConnectionPool:
    """Get the global connection pool instance"""
    global _connection_pool
    if _connection_pool is None:
        from config import Config
        app_id = app_id or Config.DERIV_APP_ID
        _connection_pool = ConnectionPool(app_id)
    return _connection_pool

async def initialize_connection_pool(app_id: str = None):
    """Initialize the global connection pool"""
    pool = get_connection_pool(app_id)
    await pool.start()
    return pool

async def cleanup_connection_pool():
    """Cleanup the global connection pool"""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.stop()
        _connection_pool = None
