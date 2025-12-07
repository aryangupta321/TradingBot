"""
Risk Management Engine - implements safety rules for trade execution.
This is the critical safety layer that prevents dangerous trades.
"""

from datetime import datetime, timedelta
from typing import Tuple, Dict, List
from collections import defaultdict
import threading

from config import Config
from csv_logger import logger


class RiskEngine:
    """
    Manages trading risk with multiple safety constraints:
    - Max risk per trade
    - Max trades per day
    - Minimum balance requirement
    - Duplicate signal cooldown
    - Confidence threshold
    """
    
    def __init__(self):
        """Initialize risk engine with empty tracking dictionaries."""
        self._lock = threading.Lock()
        
        # Track trades executed today for daily limit
        self._trades_today: List[datetime] = []
        
        # Track recent signals to prevent duplicates within cooldown period
        # Key: (symbol, action), Value: last signal datetime
        self._signal_cache: Dict[Tuple[str, str], datetime] = {}
        
        # Track open orders/positions (can be extended with actual positions)
        self._open_trades: List[Dict] = []
        
        # Reset daily counters at midnight
        self._last_reset = datetime.utcnow().date()
    
    def _reset_daily_counters(self):
        """Reset daily trade counter if day has changed."""
        today = datetime.utcnow().date()
        if today > self._last_reset:
            self._trades_today = []
            self._last_reset = today
            logger.log_info("Daily counters reset")
    
    def check_all_constraints(
        self,
        symbol: str,
        action: str,
        confidence: float,
        account_balance: float
    ) -> Tuple[bool, str]:
        """
        Check all risk constraints before allowing a trade.
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            action: BUY or SELL
            confidence: Confidence level (0-100)
            account_balance: Current USDT balance
        
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        with self._lock:
            self._reset_daily_counters()
            
            # 1. Check confidence threshold
            if confidence < Config.MIN_CONFIDENCE:
                return False, f"Confidence {confidence:.1f} below minimum {Config.MIN_CONFIDENCE}"
            
            # 2. Check minimum balance
            if account_balance < Config.MIN_BALANCE_USDT:
                return False, (
                    f"Insufficient balance: ${account_balance:.2f} < "
                    f"${Config.MIN_BALANCE_USDT} minimum"
                )
            
            # 3. Check max risk per trade
            available_for_trade = min(account_balance, Config.MAX_RISK_PER_TRADE)
            if available_for_trade <= 0:
                return False, f"Trade size ${Config.MAX_RISK_PER_TRADE} exceeds balance ${account_balance:.2f}"
            
            # 4. Check max open trades
            if len(self._open_trades) >= Config.MAX_OPEN_TRADES:
                return False, (
                    f"Max open trades {Config.MAX_OPEN_TRADES} reached "
                    f"({len(self._open_trades)} currently open)"
                )
            
            # 5. Check daily trade limit
            if len(self._trades_today) >= Config.MAX_TRADES_PER_DAY:
                return False, (
                    f"Daily trade limit {Config.MAX_TRADES_PER_DAY} reached "
                    f"({len(self._trades_today)} executed today)"
                )
            
            # 6. Check duplicate signal cooldown
            cache_key = (symbol, action)
            if cache_key in self._signal_cache:
                last_signal = self._signal_cache[cache_key]
                cooldown_expiry = last_signal + timedelta(seconds=Config.SIGNAL_COOLDOWN_SECONDS)
                
                if datetime.utcnow() < cooldown_expiry:
                    time_remaining = (cooldown_expiry - datetime.utcnow()).total_seconds()
                    return False, (
                        f"Duplicate {action} signal for {symbol}: "
                        f"cooldown active for {time_remaining:.0f}s more"
                    )
            
            # All checks passed
            return True, "All risk constraints satisfied"
    
    def record_signal(self, symbol: str, action: str):
        """
        Record that a signal was processed (for cooldown tracking).
        Call this AFTER a trade is accepted to prevent duplicates.
        
        Args:
            symbol: Trading pair
            action: BUY or SELL
        """
        with self._lock:
            cache_key = (symbol, action)
            self._signal_cache[cache_key] = datetime.utcnow()
    
    def record_trade(self, symbol: str, action: str):
        """
        Record that a trade was executed (for daily limit tracking).
        Call this AFTER the trade is confirmed filled on Binance.
        
        Args:
            symbol: Trading pair
            action: BUY or SELL
        """
        with self._lock:
            self._trades_today.append(datetime.utcnow())
            logger.log_info(
                f"Trade recorded: {action} {symbol} | "
                f"Daily: {len(self._trades_today)}/{Config.MAX_TRADES_PER_DAY}"
            )
    
    def add_open_trade(self, symbol: str, order_id: str, action: str, quantity: float):
        """
        Track an open position (optional for more advanced risk management).
        
        Args:
            symbol: Trading pair
            order_id: Binance order ID
            action: BUY or SELL
            quantity: Position size
        """
        with self._lock:
            self._open_trades.append({
                'symbol': symbol,
                'order_id': order_id,
                'action': action,
                'quantity': quantity,
                'opened_at': datetime.utcnow()
            })
    
    def remove_open_trade(self, order_id: str):
        """
        Remove a closed position from tracking.
        
        Args:
            order_id: Binance order ID to remove
        """
        with self._lock:
            self._open_trades = [t for t in self._open_trades if t['order_id'] != order_id]
    
    def get_status(self) -> Dict:
        """
        Get current risk engine status for monitoring.
        
        Returns:
            Dictionary with current limits and usage
        """
        with self._lock:
            self._reset_daily_counters()
            return {
                'trades_today': len(self._trades_today),
                'max_trades_per_day': Config.MAX_TRADES_PER_DAY,
                'open_trades': len(self._open_trades),
                'max_open_trades': Config.MAX_OPEN_TRADES,
                'max_risk_per_trade': Config.MAX_RISK_PER_TRADE,
                'min_balance': Config.MIN_BALANCE_USDT,
                'cooldown_seconds': Config.SIGNAL_COOLDOWN_SECONDS,
                'min_confidence': Config.MIN_CONFIDENCE,
            }


# Global risk engine instance
risk_engine = RiskEngine()
