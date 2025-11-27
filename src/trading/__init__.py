"""
Trading module for Deriv Telegram Bot
Contains trading utilities, strategies, and indicators
"""

from .utilities import (
    StepSystemUtilities,
    calculate_step_signal,
    calculate_volatility_signal,
    validate_trading_parameters,
    get_recommended_lot_sizes,
)
from .strategies import (
    Volatility75ScalpingStrategy,
)

__all__ = [
    'StepSystemUtilities',
    'calculate_step_signal',
    'calculate_volatility_signal',
    'validate_trading_parameters',
    'get_recommended_lot_sizes',
    'Volatility75ScalpingStrategy',
]
