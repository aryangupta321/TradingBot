"""
Exit Manager - Background task that monitors open positions and executes automatic exits.
This runs every 30 seconds to check:
1. Stop-loss levels - if price drops 1%, automatically sell
2. Take-profit levels - if price rises 2.5%, automatically sell to lock in profit
"""

import asyncio
import threading
from typing import Optional

from csv_logger import logger
from positions import position_manager
from binance_client import get_binance_client


class ExitManager:
    """Monitors and executes automatic stop-loss and take-profit exits."""
    
    def __init__(self, check_interval: int = 30):
        """
        Initialize exit manager.
        
        Args:
            check_interval: Check positions every N seconds
        """
        self.check_interval = check_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start the background monitoring thread."""
        if self.running:
            logger.log_info("Exit manager already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.log_info(f"Exit manager started (checking every {self.check_interval}s)")
    
    def stop(self):
        """Stop the background monitoring thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.log_info("Exit manager stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop - runs in background thread."""
        while self.running:
            try:
                self._check_all_positions()
            except Exception as e:
                logger.log_error(f"Error in exit manager loop: {e}")
            
            # Sleep for interval
            for _ in range(self.check_interval):
                if not self.running:
                    break
                asyncio.sleep(1)
    
    def _check_all_positions(self):
        """Check all open positions for SL/TP triggers."""
        try:
            binance = get_binance_client()
            positions = position_manager.get_open_positions()
            
            if not positions:
                return
            
            for position in positions:
                symbol = position['Symbol']
                
                # Get current price
                current_price = binance.get_current_price(symbol)
                if current_price is None:
                    continue
                
                # Update position with current price
                position_manager.update_position_price(symbol, current_price)
                
                entry_price = position['EntryPrice']
                stop_loss = position['StopLossPrice']
                take_profit = position['TakeProfitPrice']
                side = position['Side']
                quantity = position['Quantity']
                
                # Check stop-loss
                if side == "BUY" and current_price <= stop_loss:
                    logger.log_info(f"STOP-LOSS triggered for {symbol}: {current_price} <= {stop_loss}")
                    self._execute_exit(symbol, quantity, current_price, "STOP_LOSS")
                
                # Check take-profit
                elif side == "BUY" and current_price >= take_profit:
                    logger.log_info(f"TAKE-PROFIT triggered for {symbol}: {current_price} >= {take_profit}")
                    self._execute_exit(symbol, quantity, current_price, "TAKE_PROFIT")
                
                # For SELL positions (short)
                elif side == "SELL" and current_price >= stop_loss:
                    logger.log_info(f"STOP-LOSS triggered for SHORT {symbol}: {current_price} >= {stop_loss}")
                    self._execute_exit(symbol, quantity, current_price, "STOP_LOSS")
                
                elif side == "SELL" and current_price <= take_profit:
                    logger.log_info(f"TAKE-PROFIT triggered for SHORT {symbol}: {current_price} <= {take_profit}")
                    self._execute_exit(symbol, quantity, current_price, "TAKE_PROFIT")
        
        except Exception as e:
            logger.log_error(f"Error checking positions: {e}")
    
    def _execute_exit(self, symbol: str, quantity: float, exit_price: float, exit_type: str):
        """
        Execute position exit (stop-loss or take-profit).
        
        Args:
            symbol: Trading pair
            quantity: Position size to close
            exit_price: Price to execute at
            exit_type: STOP_LOSS or TAKE_PROFIT
        """
        try:
            binance = get_binance_client()
            
            # Determine action based on position
            positions = position_manager.get_open_positions()
            position = next((p for p in positions if p['Symbol'] == symbol), None)
            
            if not position:
                return
            
            # Execute SELL order to close position
            logger.log_info(f"Executing {exit_type} exit: SELL {quantity:.8f} {symbol}")
            order = binance.place_sell_order(symbol, quantity)
            
            if order and (order.get('status') == 'FILLED' or float(order.get('executedQty', 0)) > 0):
                executed_qty = float(order.get('executedQty', quantity))
                actual_exit_price = float(order.get('cummulativeQuoteAssetTransactedQty', 0)) / executed_qty if executed_qty > 0 else exit_price
                
                # Close position and calculate P&L
                pnl = position_manager.close_position(symbol, actual_exit_price, exit_type)
                
                if pnl is not None:
                    logger.log_info(f"{exit_type} executed: P&L = {pnl:.2f} USDT")
                else:
                    logger.log_error(f"Failed to close position for {exit_type}")
            else:
                logger.log_error(f"Failed to execute {exit_type} order for {symbol}")
        
        except Exception as e:
            logger.log_error(f"Error executing {exit_type} exit: {e}")


# Global exit manager instance
exit_manager = ExitManager(check_interval=30)
