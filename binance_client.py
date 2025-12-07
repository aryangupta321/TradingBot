"""
Binance API Client - wrapper around python-binance with testnet support.
Handles all trading operations with proper error handling and logging.
"""

from typing import Dict, Optional, Tuple
import requests
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException, BinanceOrderException

from config import Config
from csv_logger import logger


class BinanceAPIClient:
    """
    Secure wrapper around Binance API for trading operations.
    Supports both testnet and live trading.
    """
    
    def __init__(self):
        """Initialize Binance client with configured API credentials."""
        try:
            # Initialize the Binance client
            self.client = BinanceClient(
                api_key=Config.BINANCE_API_KEY,
                api_secret=Config.BINANCE_API_SECRET,
                testnet=Config.USE_TESTNET
            )
            # If a custom base URL is provided in env, override the client's API URL
            if getattr(Config, 'BINANCE_BASE_URL', None):
                try:
                    # python-binance expects API_URL to point at the API root (usually ends with '/api')
                    base = Config.BINANCE_BASE_URL.rstrip('/')
                    api_url = base if base.endswith('/api') else base + '/api'
                    # Set the client's API_URL to the configured value (best-effort)
                    self.client.API_URL = api_url
                    logger.log_info(f"Overriding Binance API URL with: {api_url}")
                except Exception:
                    # best-effort; continue without failing
                    logger.log_info("Could not override Binance client API_URL property; continuing with default.")
            
            # Test connection and credentials
            self._test_connection()
            
            logger.log_info(
                f"Binance client initialized | "
                f"Mode: {'TESTNET' if Config.USE_TESTNET else 'LIVE'}"
            )
        except Exception as e:
            logger.log_error(f"Failed to initialize Binance client: {e}")
            raise
    
    def _test_connection(self):
        """Test API credentials and connection."""
        try:
            # Simple ping to verify credentials
            self.client.ping()
        except BinanceAPIException as e:
            raise ValueError(f"Binance API authentication failed: {e}")
        except Exception as e:
            raise ValueError(f"Cannot connect to Binance API: {e}")
    
    def get_account_balance(self, asset: str = "USDT") -> float:
        """
        Get current balance for a specific asset.
        
        Args:
            asset: Asset symbol (default: USDT)
        
        Returns:
            Available balance as float, or 0.0 if not found or error
        """
        try:
            account = self.client.get_account()
            
            # Find the asset in balances
            for balance in account.get('balances', []):
                if balance['asset'] == asset:
                    available = float(balance['free'])
                    logger.log_info(f"Account balance: {available:.2f} {asset}")
                    return available
            
            logger.log_info(f"Asset {asset} not found in account")
            return 0.0
        
        except BinanceAPIException as e:
            logger.log_error(f"Failed to get account balance: {e}")
            return 0.0
        except Exception as e:
            logger.log_error(f"Unexpected error getting balance: {e}")
            return 0.0
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Get symbol information (min notional, precision, etc).
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
        
        Returns:
            Symbol info dict, or None if error
        """
        try:
            # Get exchange info which contains all symbols
            exchange_info = self.client.get_exchange_info()
            
            for sym_info in exchange_info.get('symbols', []):
                if sym_info['symbol'] == symbol:
                    return sym_info
            
            logger.log_error(f"Symbol {symbol} not found on exchange")
            return None
        
        except Exception as e:
            logger.log_error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get the current price for a symbol.
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
        
        Returns:
            Current price as float, or None if error
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.log_error(f"Failed to get price for {symbol}: {e}")
            return None
        except Exception as e:
            logger.log_error(f"Unexpected error getting price: {e}")
            return None
    
    def calculate_buy_quantity(self, symbol: str, usdt_amount: float) -> Optional[float]:
        """
        Calculate the correct quantity for a buy order based on USDT amount.
        Takes into account precision and minimum notional value.
        
        Args:
            symbol: Trading pair
            usdt_amount: Amount in USDT to spend
        
        Returns:
            Quantity to order, or None if validation fails
        """
        try:
            # Get current price
            price = self.get_current_price(symbol)
            if price is None or price == 0:
                logger.log_error(f"Cannot get price for {symbol}")
                return None
            
            # Get symbol info for precision
            symbol_info = self.get_symbol_info(symbol)
            if symbol_info is None:
                return None
            
            # Calculate quantity
            raw_quantity = usdt_amount / price
            
            # Get base asset precision
            base_precision = next(
                (f['stepSize'] for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'),
                None
            )
            
            if base_precision is None:
                logger.log_error(f"Cannot determine precision for {symbol}")
                return None
            
            # Round to precision
            precision = len(base_precision.rstrip('0').split('.')[-1]) if '.' in base_precision else 0
            quantity = round(raw_quantity, precision)
            
            # Validate minimum notional
            min_notional = next(
                (float(f['minNotional']) for f in symbol_info['filters'] 
                 if f['filterType'] == 'MIN_NOTIONAL'),
                0
            )
            
            if (quantity * price) < min_notional:
                logger.log_error(
                    f"Order size ${quantity * price:.2f} below minimum ${min_notional:.2f}"
                )
                return None
            
            return quantity
        
        except Exception as e:
            logger.log_error(f"Error calculating buy quantity: {e}")
            return None
    
    def place_buy_order(
        self,
        symbol: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Place a buy order on Binance.
        Uses MARKET order for speed, LIMIT order if price specified.
        
        Args:
            symbol: Trading pair
            quantity: Amount to buy
            price: Optional limit price (None = market order)
        
        Returns:
            Order dict with details, or None if failed
        """
        try:
            if price is None:
                # Market order - executes immediately at best available price
                logger.log_info(f"Placing MARKET BUY order: {quantity} {symbol}")
                order = self.client.order_market_buy(
                    symbol=symbol,
                    quantity=quantity
                )
            else:
                # Limit order - executes only at specified price or better
                logger.log_info(f"Placing LIMIT BUY order: {quantity} {symbol} @ ${price}")
                order = self.client.order_limit_buy(
                    symbol=symbol,
                    quantity=quantity,
                    price=price
                )
            
            order_id = order.get('orderId')
            logger.log_info(f"Order placed successfully: ID {order_id}")
            return order
        
        except BinanceOrderException as e:
            logger.log_error(f"Binance order error for {symbol}: {e}")
            return None
        except BinanceAPIException as e:
            logger.log_error(f"Binance API error placing order: {e}")
            return None
        except Exception as e:
            logger.log_error(f"Unexpected error placing buy order: {e}")
            return None
    
    def place_sell_order(
        self,
        symbol: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Place a sell order on Binance.
        Uses MARKET order for speed, LIMIT order if price specified.
        
        Args:
            symbol: Trading pair
            quantity: Amount to sell
            price: Optional limit price (None = market order)
        
        Returns:
            Order dict with details, or None if failed
        """
        try:
            if price is None:
                # Market order
                logger.log_info(f"Placing MARKET SELL order: {quantity} {symbol}")
                order = self.client.order_market_sell(
                    symbol=symbol,
                    quantity=quantity
                )
            else:
                # Limit order
                logger.log_info(f"Placing LIMIT SELL order: {quantity} {symbol} @ ${price}")
                order = self.client.order_limit_sell(
                    symbol=symbol,
                    quantity=quantity,
                    price=price
                )
            
            order_id = order.get('orderId')
            logger.log_info(f"Order placed successfully: ID {order_id}")
            return order
        
        except BinanceOrderException as e:
            logger.log_error(f"Binance order error for {symbol}: {e}")
            return None
        except BinanceAPIException as e:
            logger.log_error(f"Binance API error placing order: {e}")
            return None
        except Exception as e:
            logger.log_error(f"Unexpected error placing sell order: {e}")
            return None
    
    def get_order_status(self, symbol: str, order_id: int) -> Optional[str]:
        """
        Check the status of an order.
        
        Args:
            symbol: Trading pair
            order_id: Binance order ID
        
        Returns:
            Order status (NEW, PARTIALLY_FILLED, FILLED, CANCELED, etc), or None if error
        """
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            return order.get('status')
        except Exception as e:
            logger.log_error(f"Error checking order status: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """
        Cancel an open order.
        
        Args:
            symbol: Trading pair
            order_id: Binance order ID
        
        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            self.client.cancel_order(symbol=symbol, orderId=order_id)
            logger.log_info(f"Order {order_id} cancelled successfully")
            return True
        except Exception as e:
            logger.log_error(f"Error cancelling order {order_id}: {e}")
            return False


# Global Binance client instance
binance_client: Optional[BinanceAPIClient] = None


def initialize_binance_client() -> bool:
    """
    Initialize the global Binance client.
    Returns True on success, False on failure.
    """
    global binance_client
    try:
        binance_client = BinanceAPIClient()
        return True
    except Exception as e:
        logger.log_error(f"Failed to initialize Binance client: {e}")
        return False


def get_binance_client() -> Optional[BinanceAPIClient]:
    """Get the global Binance client instance."""
    return binance_client
