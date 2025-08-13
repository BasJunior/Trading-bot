#!/usr/bin/env python3
"""
User Management Module for Deriv Telegram Bot
Handles user authentication, session management, and account tracking
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """User session data"""
    user_id: int
    username: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: str
    last_seen: str
    api_token: Optional[str] = None
    account_balance: Optional[float] = None
    total_trades: int = 0
    successful_trades: int = 0
    total_profit: float = 0.0
    active_strategies: List[str] = None
    
    def __post_init__(self):
        if self.active_strategies is None:
            self.active_strategies = []

class UserManager:
    """Manages user sessions and data"""
    
    def __init__(self, data_file: str = "user_data.json"):
        self.data_file = data_file
        self.users: Dict[int, UserSession] = {}
        self.load_users()
    
    def load_users(self):
        """Load user data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for user_id, user_data in data.items():
                        self.users[int(user_id)] = UserSession(**user_data)
                logger.info(f"Loaded {len(self.users)} users from {self.data_file}")
        except Exception as e:
            logger.error(f"Error loading users: {e}")
    
    def save_users(self):
        """Save user data to file"""
        try:
            data = {}
            for user_id, user_session in self.users.items():
                data[user_id] = asdict(user_session)
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.users)} users to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = "") -> UserSession:
        """Add a new user or update existing user"""
        now = datetime.now().isoformat()
        
        if user_id in self.users:
            # Update existing user
            user = self.users[user_id]
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.last_seen = now
            user.is_active = True
        else:
            # Create new user
            user = UserSession(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                created_at=now,
                last_seen=now
            )
            self.users[user_id] = user
        
        self.save_users()
        return user
    
    def get_user(self, user_id: int) -> Optional[UserSession]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user_activity(self, user_id: int):
        """Update user's last seen time"""
        if user_id in self.users:
            self.users[user_id].last_seen = datetime.now().isoformat()
            self.save_users()
    
    def set_user_api_token(self, user_id: int, api_token: str):
        """Set user's Deriv API token"""
        if user_id in self.users:
            self.users[user_id].api_token = api_token
            self.save_users()
    
    def remove_user_api_token(self, user_id: int):
        """Remove user's Deriv API token"""
        if user_id in self.users:
            self.users[user_id].api_token = None
            self.save_users()
    
    def update_user_balance(self, user_id: int, balance: float):
        """Update user's account balance"""
        if user_id in self.users:
            self.users[user_id].account_balance = balance
            self.save_users()
    
    def add_trade_result(self, user_id: int, profit: float, is_successful: bool):
        """Add a trade result for a user"""
        if user_id in self.users:
            user = self.users[user_id]
            user.total_trades += 1
            user.total_profit += profit
            if is_successful:
                user.successful_trades += 1
            self.save_users()
    
    def add_active_strategy(self, user_id: int, strategy_name: str):
        """Add an active strategy for a user"""
        if user_id in self.users:
            user = self.users[user_id]
            if strategy_name not in user.active_strategies:
                user.active_strategies.append(strategy_name)
                self.save_users()
    
    def remove_active_strategy(self, user_id: int, strategy_name: str):
        """Remove an active strategy for a user"""
        if user_id in self.users:
            user = self.users[user_id]
            if strategy_name in user.active_strategies:
                user.active_strategies.remove(strategy_name)
                self.save_users()
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        if user_id not in self.users:
            return {}
        
        user = self.users[user_id]
        win_rate = (user.successful_trades / user.total_trades * 100) if user.total_trades > 0 else 0
        
        return {
            'total_trades': user.total_trades,
            'successful_trades': user.successful_trades,
            'failed_trades': user.total_trades - user.successful_trades,
            'win_rate': win_rate,
            'total_profit': user.total_profit,
            'average_profit': user.total_profit / user.total_trades if user.total_trades > 0 else 0,
            'active_strategies': len(user.active_strategies),
            'member_since': user.created_at
        }
    
    def get_all_users(self) -> List[UserSession]:
        """Get all users"""
        return list(self.users.values())
    
    def get_active_users(self, hours: int = 24) -> List[UserSession]:
        """Get users active within specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        active_users = []
        
        for user in self.users.values():
            last_seen = datetime.fromisoformat(user.last_seen)
            if last_seen > cutoff_time:
                active_users.append(user)
        
        return active_users
    
    def get_users_with_strategies(self) -> List[UserSession]:
        """Get users with active strategies"""
        return [user for user in self.users.values() if user.active_strategies]
    
    def cleanup_inactive_users(self, days: int = 30):
        """Remove users inactive for specified days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        inactive_users = []
        
        for user_id, user in self.users.items():
            last_seen = datetime.fromisoformat(user.last_seen)
            if last_seen < cutoff_time:
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            del self.users[user_id]
        
        if inactive_users:
            self.save_users()
            logger.info(f"Cleaned up {len(inactive_users)} inactive users")
        
        return len(inactive_users)

# Global user manager instance
user_manager = UserManager()

# Convenience functions
def add_user(user_id: int, username: str, first_name: str, last_name: str = "") -> UserSession:
    """Add a new user"""
    return user_manager.add_user(user_id, username, first_name, last_name)

def get_user(user_id: int) -> Optional[UserSession]:
    """Get user by ID"""
    return user_manager.get_user(user_id)

def update_user_activity(user_id: int):
    """Update user's last seen time"""
    user_manager.update_user_activity(user_id)

def set_user_api_token(user_id: int, api_token: str):
    """Set user's API token"""
    user_manager.set_user_api_token(user_id, api_token)

def remove_user_api_token(user_id: int):
    """Remove user's API token"""
    user_manager.remove_user_api_token(user_id)

def get_user_stats(user_id: int) -> Dict:
    """Get user statistics"""
    return user_manager.get_user_stats(user_id)

if __name__ == "__main__":
    # Test the user manager
    print("Testing User Manager...")
    
    # Test adding users
    user1 = add_user(123456, "testuser", "Test", "User")
    print(f"Added user: {user1}")
    
    # Test getting user
    retrieved_user = get_user(123456)
    print(f"Retrieved user: {retrieved_user}")
    
    # Test user stats
    stats = get_user_stats(123456)
    print(f"User stats: {stats}")
    
    print("User Manager test completed!")
