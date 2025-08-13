#!/usr/bin/env python3
"""
Simple test to verify class creation and attribute setting
"""

class TestBot:
    def __init__(self):
        print("DEBUG: TestBot.__init__ called")
        self.test_attr = "test_value"
        print("DEBUG: test_attr set")

def test_simple_class():
    print("Creating TestBot...")
    bot = TestBot()
    print(f"TestBot created, has test_attr: {hasattr(bot, 'test_attr')}")
    if hasattr(bot, 'test_attr'):
        print(f"test_attr value: {bot.test_attr}")

if __name__ == "__main__":
    test_simple_class()
