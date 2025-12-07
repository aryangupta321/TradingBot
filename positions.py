"""
Position Manager - Tracks open trades and manages exit logic (stop-loss and take-profit).
This is the CRITICAL piece that was missing - automatic profit taking and loss prevention.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import threading

from config import Config
from csv_logger import logger


class PositionManager:
    """Manages all open trading positions with automatic SL/TP exits."""
    
    def __init__(self):
        """Initialize position manager."""
        self._lock = threading.Lock()
        self.positions_file = Path(Config.PROJECT_ROOT) / "logs" / "positions.csv"
        self._ensure_positions_file()
    
    def _ensure_positions_file(self):
        """Create positions.csv if it doesn't exist."""
        if not self.positions_file.exists():
            try:
                with open(self.positions_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=[
                            'EntryTime', 'Symbol', 'Side', 'Quantity', 'EntryPrice',
                            'StopLossPrice', 'TakeProfitPrice', 'CurrentPrice',
                            'Status', 'ExitTime', 'ExitPrice', 'PnL', 'PnLPercent'
                        ]
                    )
                    writer.writeheader()
                logger.log_info("Created positions.csv for tracking open trades")
            except Exception as e:
                logger.log_error(f"Failed to create positions file: {e}")
    
    def open_position(
        self,
        symbol: str,
        side: str,
        quantity: float,
        entry_price: float
    ) -> bool:
        """
        Record a new open position.
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Amount bought/sold
            entry_price: Entry price in USDT
        
        Returns:
            True if recorded successfully
        """
        try:
            with self._lock:
                # Calculate SL and TP
                if side == "BUY":
                    stop_loss = entry_price * 0.99  # 1% below entry
                    take_profit = entry_price * 1.025  # 2.5% above entry
                else:  # SELL
                    stop_loss = entry_price * 1.01  # 1% above entry (for short)
                    take_profit = entry_price * 0.975  # 2.5% below entry (for short)
                
                row = {
                    'EntryTime': datetime.utcnow().isoformat(),
                    'Symbol': symbol,
                    'Side': side,
                    'Quantity': f"{quantity:.8f}",
                    'EntryPrice': f"{entry_price:.2f}",
                    'StopLossPrice': f"{stop_loss:.2f}",
                    'TakeProfitPrice': f"{take_profit:.2f}",
                    'CurrentPrice': f"{entry_price:.2f}",
                    'Status': 'OPEN',
                    'ExitTime': '',
                    'ExitPrice': '',
                    'PnL': '',
                    'PnLPercent': ''
                }
                
                with open(self.positions_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=row.keys())
                    writer.writerow(row)
                
                logger.log_info(
                    f"Position opened: {side} {quantity:.8f} {symbol} @ {entry_price:.2f} "
                    f"| SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
                )
                return True
        
        except Exception as e:
            logger.log_error(f"Failed to open position: {e}")
            return False
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions.
        
        Returns:
            List of open position dictionaries
        """
        try:
            with self._lock:
                positions = []
                if self.positions_file.exists():
                    with open(self.positions_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get('Status') == 'OPEN':
                                # Convert strings to numbers
                                row['Quantity'] = float(row['Quantity'])
                                row['EntryPrice'] = float(row['EntryPrice'])
                                row['StopLossPrice'] = float(row['StopLossPrice'])
                                row['TakeProfitPrice'] = float(row['TakeProfitPrice'])
                                row['CurrentPrice'] = float(row.get('CurrentPrice', row['EntryPrice']))
                                positions.append(row)
                return positions
        except Exception as e:
            logger.log_error(f"Failed to get open positions: {e}")
            return []
    
    def update_position_price(self, symbol: str, current_price: float) -> bool:
        """Update current price for a position."""
        try:
            with self._lock:
                positions = []
                with open(self.positions_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['Symbol'] == symbol and row['Status'] == 'OPEN':
                            row['CurrentPrice'] = f"{current_price:.2f}"
                        positions.append(row)
                
                with open(self.positions_file, 'w', newline='', encoding='utf-8') as f:
                    if positions:
                        writer = csv.DictWriter(f, fieldnames=positions[0].keys())
                        writer.writeheader()
                        writer.writerows(positions)
                
                return True
        except Exception as e:
            logger.log_error(f"Failed to update position price: {e}")
            return False
    
    def close_position(
        self,
        symbol: str,
        exit_price: float,
        exit_type: str = "MANUAL"
    ) -> Optional[float]:
        """
        Close a position and calculate P&L.
        
        Args:
            symbol: Trading pair
            exit_price: Price at which position was closed
            exit_type: Reason for exit (MANUAL, STOP_LOSS, TAKE_PROFIT)
        
        Returns:
            P&L amount, or None if failed
        """
        try:
            with self._lock:
                positions = []
                pnl = None
                
                with open(self.positions_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['Symbol'] == symbol and row['Status'] == 'OPEN':
                            # Calculate P&L
                            entry_price = float(row['EntryPrice'])
                            quantity = float(row['Quantity'])
                            side = row['Side']
                            
                            if side == "BUY":
                                pnl = (exit_price - entry_price) * quantity
                                pnl_percent = ((exit_price - entry_price) / entry_price) * 100
                            else:  # SELL
                                pnl = (entry_price - exit_price) * quantity
                                pnl_percent = ((entry_price - exit_price) / entry_price) * 100
                            
                            # Update position
                            row['Status'] = 'CLOSED'
                            row['ExitTime'] = datetime.utcnow().isoformat()
                            row['ExitPrice'] = f"{exit_price:.2f}"
                            row['PnL'] = f"{pnl:.2f}"
                            row['PnLPercent'] = f"{pnl_percent:.2f}%"
                            
                            logger.log_info(
                                f"Position closed: {side} {quantity:.8f} {symbol} "
                                f"@ {exit_price:.2f} | P&L: {pnl:.2f} USDT ({pnl_percent:.2f}%)"
                            )
                        
                        positions.append(row)
                
                with open(self.positions_file, 'w', newline='', encoding='utf-8') as f:
                    if positions:
                        writer = csv.DictWriter(f, fieldnames=positions[0].keys())
                        writer.writeheader()
                        writer.writerows(positions)
                
                return pnl
        
        except Exception as e:
            logger.log_error(f"Failed to close position: {e}")
            return None


# Global position manager instance
position_manager = PositionManager()
