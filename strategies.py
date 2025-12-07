"""
Trading Strategies for Scalping and Swing Trading.

This module defines two distinct trading strategies with different parameters,
risk profiles, and signal interpretation rules. Both are designed to maximize
win rate and profitability within their respective time horizons.
"""

class ScalpingStrategy:
    """
    Scalping Strategy: Short-term trades (seconds to minutes)
    
    Characteristics:
    - Very short holding periods (1-5 minutes)
    - High frequency of trades (10-50+ per day)
    - Tight stop-losses (0.1-0.5% below entry)
    - Quick profit targets (0.2-1% above entry)
    - Requires high win rate (70%+ to be profitable after fees)
    - Works best in volatile, liquid markets (BTC, ETH, major altcoins)
    
    Risk Profile: HIGH frequency, SMALL position size
    Best for: Intraday traders with active monitoring
    """
    
    name = "Scalping"
    timeframe = "1m"  # 1-minute candles
    
    # Signal validation
    min_confidence = 75  # Require high confidence for fast trades
    
    # Position sizing
    max_risk_per_trade = 2  # Risk $2 per scalp trade
    max_position_size = 0.5  # Small positions to limit slippage
    max_open_trades = 5  # Can have 5 scalps open simultaneously
    max_trades_per_day = 50  # 50+ scalps per day is realistic
    
    # Stop-loss and take-profit
    stop_loss_percent = 0.3  # Tight: 0.3% below entry
    take_profit_percent = 0.5  # Quick profit: 0.5% above entry
    
    # Cooldown between same symbol
    signal_cooldown_seconds = 5  # Can re-enter same symbol after 5 seconds
    
    # Symbols suitable for scalping
    suitable_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']
    
    description = """
    SCALPING STRATEGY
    ================
    
    Ideal for: Short-term traders who can monitor charts actively
    
    Key Rules:
    - Enter on strong momentum (confidence 75%+)
    - Exit immediately on 0.5% profit OR 0.3% loss
    - Average 10-50 trades per day
    - Hold positions for 1-5 minutes
    - Trade only liquid pairs (BTC, ETH, major alts)
    
    TradingView Setup:
    - Use 1-minute candles
    - Watch RSI (30-70 levels) for momentum
    - Confirm with MACD crossovers
    - Set take-profit at 0.5% and stop-loss at 0.3%
    - Use alert frequency: Every 1 minute
    
    Win Rate Target: 70%+ (due to tight stops)
    Expected Daily P&L: $10-50 per scalp cycle (depends on capital)
    """


class SwingTradingStrategy:
    """
    Swing Trading Strategy: Medium-term trades (hours to days)
    
    Characteristics:
    - Medium holding periods (4 hours to 3 days)
    - Moderate frequency (2-10 trades per day)
    - Wider stop-losses (1-3% below entry)
    - Larger profit targets (2-5% above entry)
    - Can work with lower win rate (50-60% still profitable)
    - Works on any liquid pair, including altcoins
    
    Risk Profile: MODERATE frequency, MEDIUM position size
    Best for: Semi-active traders with daily monitoring
    """
    
    name = "Swing Trading"
    timeframe = "4h"  # 4-hour candles
    
    # Signal validation
    min_confidence = 65  # Lower confidence OK due to longer holds
    
    # Position sizing
    max_risk_per_trade = 5  # Risk $5 per swing trade
    max_position_size = 2.0  # Larger positions; liquidity allows
    max_open_trades = 3  # Fewer concurrent positions
    max_trades_per_day = 10  # 5-10 swings per day
    
    # Stop-loss and take-profit
    stop_loss_percent = 2.0  # Wider: 2% below entry
    take_profit_percent = 3.0  # Larger profit: 3% above entry
    
    # Cooldown between same symbol
    signal_cooldown_seconds = 300  # Wait 5 minutes before re-entering same symbol
    
    # Symbols suitable for swing trading
    suitable_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT', 'SOLUSDT']
    
    description = """
    SWING TRADING STRATEGY
    ======================
    
    Ideal for: Part-time traders who check charts 2-3x per day
    
    Key Rules:
    - Enter on confirmed support/resistance breakout (confidence 65%+)
    - Exit on 3% profit OR 2% loss
    - Average 5-10 trades per day
    - Hold positions for 4 hours to 3 days
    - Trade liquid pairs with clear support/resistance
    
    TradingView Setup:
    - Use 4-hour candles (or daily for longer swings)
    - Watch moving averages (20 & 50 SMA for trend)
    - Confirm with Bollinger Bands (oversold/overbought)
    - Set take-profit at 3% and stop-loss at 2%
    - Use alert frequency: Every 4 hours
    
    Win Rate Target: 55-60% (wider stops mean higher loss trades)
    Expected Daily P&L: $50-200 per swing (depends on capital and luck)
    """


# Quick reference
STRATEGIES = {
    'scalping': ScalpingStrategy,
    'swing': SwingTradingStrategy,
}

if __name__ == '__main__':
    print(ScalpingStrategy.description)
    print('\n' + '='*80 + '\n')
    print(SwingTradingStrategy.description)
