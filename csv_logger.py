"""
CSV Logger module - handles all logging to CSV files for human-readable analysis.
Uses simple CSV format compatible with Excel and data analysis tools.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import threading

from config import Config


class CSVLogger:
    """Thread-safe CSV logger for signals and trades."""
    
    def __init__(self):
        """Initialize CSV logger and create headers if files don't exist."""
        self._lock = threading.Lock()  # Thread safety for concurrent writes
        self._ensure_csv_files()
    
    def _ensure_csv_files(self):
        """Create CSV files with headers if they don't exist."""
        # Signals CSV
        if not Config.SIGNALS_CSV.exists():
            self._write_signals_header()
        
        # Trades CSV
        if not Config.TRADES_CSV.exists():
            self._write_trades_header()
    
    def _write_signals_header(self):
        """Write header row for signals.csv"""
        try:
            with open(Config.SIGNALS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        'DateTime', 'TradingPair', 'Action', 'Strategy',
                        'TimeFrame', 'Confidence', 'Decision', 'Reason'
                    ]
                )
                writer.writeheader()
        except Exception as e:
            print(f"ERROR writing signals header: {e}")
    
    def _write_trades_header(self):
        """Write header row for trades.csv"""
        try:
            with open(Config.TRADES_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        'DateTime', 'TradingPair', 'Action', 'TradeAmount',
                        'Price', 'OrderID', 'Status'
                    ]
                )
                writer.writeheader()
        except Exception as e:
            print(f"ERROR writing trades header: {e}")
    
    def log_signal(
        self,
        symbol: str,
        action: str,
        strategy: str,
        timeframe: str,
        confidence: float,
        decision: str,
        reason: str
    ):
        """
        Log a trading signal to signals.csv
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            action: BUY or SELL
            strategy: Strategy name from signal
            timeframe: Timeframe (e.g., 4h, 1d)
            confidence: Confidence level (0-100)
            decision: ACCEPTED or REJECTED
            reason: Human-readable reason for decision
        """
        with self._lock:
            try:
                row = {
                    'DateTime': datetime.utcnow().isoformat(),
                    'TradingPair': symbol,
                    'Action': action,
                    'Strategy': strategy,
                    'TimeFrame': timeframe,
                    'Confidence': f"{confidence:.1f}",
                    'Decision': decision,
                    'Reason': reason
                }
                
                with open(Config.SIGNALS_CSV, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=[
                            'DateTime', 'TradingPair', 'Action', 'Strategy',
                            'TimeFrame', 'Confidence', 'Decision', 'Reason'
                        ]
                    )
                    writer.writerow(row)
            except Exception as e:
                print(f"ERROR logging signal: {e}")
    
    def log_trade(
        self,
        symbol: str,
        action: str,
        quantity: float,
        price: float,
        order_id: str,
        status: str = "PENDING"
    ):
        """
        Log a trade execution to trades.csv
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            action: BUY or SELL
            quantity: Amount of asset traded
            price: Execution price in USDT
            order_id: Binance order ID
            status: Order status (PENDING, FILLED, FAILED, CANCELLED)
        """
        with self._lock:
            try:
                trade_amount = quantity * price  # Total value in USDT
                
                row = {
                    'DateTime': datetime.utcnow().isoformat(),
                    'TradingPair': symbol,
                    'Action': action,
                    'TradeAmount': f"{trade_amount:.2f}",
                    'Price': f"{price:.8f}",
                    'OrderID': order_id,
                    'Status': status
                }
                
                with open(Config.TRADES_CSV, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=[
                            'DateTime', 'TradingPair', 'Action', 'TradeAmount',
                            'Price', 'OrderID', 'Status'
                        ]
                    )
                    writer.writerow(row)
            except Exception as e:
                print(f"ERROR logging trade: {e}")
    
    def log_error(self, message: str):
        """Log an error message to console (could extend to file)."""
        timestamp = datetime.utcnow().isoformat()
        print(f"[ERROR {timestamp}] {message}")
    
    def log_info(self, message: str):
        """Log an info message to console."""
        timestamp = datetime.utcnow().isoformat()
        print(f"[INFO {timestamp}] {message}")


# Global logger instance
logger = CSVLogger()
