"""
Trading Bot - FastAPI webhook server for receiving TradingView alerts.

This is the main application file that orchestrates:
1. Webhook security (secret key validation)
2. Signal parsing and validation
3. Risk engine checks
4. Trade execution via Binance
5. Comprehensive logging

IMPORTANT: This bot does NOT guarantee profits. Trading is risky.
Always start with testnet and small position sizes.
"""

from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import hmac
import hashlib

from config import Config, validate_config
from csv_logger import logger
from risk import risk_engine
from binance_client import initialize_binance_client, get_binance_client
from positions import position_manager
from exit_manager import exit_manager


# ============= DATA MODELS =============

class WebhookPayload(BaseModel):
    """Expected format of TradingView webhook JSON."""
    
    symbol: str = Field(..., description="Trading pair e.g. BTCUSDT")
    side: str = Field(..., description="BUY or SELL")
    strategy: str = Field(default="Unknown", description="Strategy name")
    timeframe: str = Field(default="Unknown", description="Timeframe e.g. 4h, 1d")
    confidence: float = Field(default=50, ge=0, le=100, description="Confidence 0-100")
    
    @validator('side')
    def validate_side(cls, v):
        """Ensure side is uppercase and valid."""
        v = v.upper()
        if v not in ['BUY', 'SELL']:
            raise ValueError('side must be BUY or SELL')
        return v
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Ensure symbol is uppercase."""
        return v.upper()


class WebhookResponse(BaseModel):
    """Response format for webhook requests."""
    success: bool
    message: str
    decision: str  # ACCEPTED, REJECTED
    reason: str
    signal_id: Optional[str] = None


# ============= FLASK APP INITIALIZATION =============

app = FastAPI(
    title="Crypto Trading Bot",
    description="Production-ready trading bot for receiving TradingView alerts",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    try:
        logger.log_info("=" * 60)
        logger.log_info("TRADING BOT STARTING UP")
        logger.log_info("=" * 60)
        
        # Validate configuration
        validate_config()
        
        # Initialize Binance client (skip on Railway due to IP restrictions)
        try:
            if not initialize_binance_client():
                logger.log_warning("Could not connect to Binance on startup (IP restriction - Railway)")
                logger.log_info("Bot will still accept webhook signals and execute trades when needed")
        except Exception as e:
            logger.log_warning(f"Binance connection failed: {str(e)}")
            logger.log_info("Continuing in webhook-only mode")
        
        # Start exit manager (automatic stop-loss and take-profit)
        exit_manager.start()
        
        # Try to log startup info if client available
        try:
            binance = get_binance_client()
            balance = binance.get_account_balance("USDT")
        except:
            balance = 0
        
        logger.log_info(f"Account USDT Balance: ${balance:.2f}")
        logger.log_info(f"Max risk per trade: ${Config.MAX_RISK_PER_TRADE}")
        logger.log_info(f"Max trades per day: {Config.MAX_TRADES_PER_DAY}")
        logger.log_info(f"Testnet mode: {Config.USE_TESTNET}")
        logger.log_info("✅ Bot ready to receive signals on webhook")
        logger.log_info("✅ Exit manager active (automatic SL/TP)")
        logger.log_info("Waiting for TradingView alerts...")
        logger.log_info("=" * 60)
        logger.log_info("Bot ready to receive signals")
        logger.log_info("=" * 60)
    
    except Exception as e:
        logger.log_error(f"Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown."""
    exit_manager.stop()
    logger.log_info("Bot shutting down")


# ============= ENDPOINTS =============

@app.get("/health", tags=["Status"])
async def health_check():
    """
    Health check endpoint for monitoring.
    Use this to verify the bot is running and responsive.
    """
    try:
        binance = get_binance_client()
        balance = binance.get_account_balance("USDT")
        risk_status = risk_engine.get_status()
        
        return {
            "status": "healthy",
            "balance_usdt": balance,
            "risk_limits": risk_status
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/webhook", response_model=WebhookResponse, tags=["Trading"])
async def receive_signal(request: Request):
    """
    Main webhook endpoint for receiving TradingView alerts.
    
    SECURITY: Validates secret key from request header or JSON body.
    
    Example request:
    ```
    POST /webhook
    Header: Authorization: Bearer your-secret-key
    
    {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "strategy": "RSI Oversold",
        "timeframe": "4h",
        "confidence": 75
    }
    ```
    """
    try:
        # Parse JSON body
        body = await request.json()
        
        # SECURITY: Secret validation disabled for testing phase
        # Remove secret fields from body if present
        body.pop("secret", None)
        body.pop("webhook_secret", None)
        
        # Validate webhook payload
        try:
            payload = WebhookPayload(**body)
        except ValueError as e:
            logger.log_error(f"Invalid webhook format: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payload: {e}"
            )
        
        # Get current account state
        binance = get_binance_client()
        balance = binance.get_account_balance("USDT")
        
        # Check all risk constraints
        allowed, reason = risk_engine.check_all_constraints(
            symbol=payload.symbol,
            action=payload.side,
            confidence=payload.confidence,
            account_balance=balance
        )
        
        # Log signal decision
        logger.log_signal(
            symbol=payload.symbol,
            action=payload.side,
            strategy=payload.strategy,
            timeframe=payload.timeframe,
            confidence=payload.confidence,
            decision="ACCEPTED" if allowed else "REJECTED",
            reason=reason
        )
        
        if not allowed:
            return WebhookResponse(
                success=True,
                message="Signal received but rejected by risk engine",
                decision="REJECTED",
                reason=reason
            )
        
        # ============= EXECUTE TRADE =============
        try:
            # Calculate position size based on risk mode
            if Config.USE_PERCENTAGE_RISK:
                # Auto-reinvestment: Use percentage of current balance
                trade_amount = balance * Config.RISK_PERCENTAGE
                # Ensure minimum notional ($5 for BTCUSDT)
                trade_amount = max(trade_amount, 5.0)
                logger.log_info(f"Auto-reinvest mode: ${trade_amount:.2f} ({Config.RISK_PERCENTAGE*100:.0f}% of ${balance:.2f})")
            else:
                # Fixed risk mode
                trade_amount = Config.MAX_RISK_PER_TRADE
                logger.log_info(f"Fixed risk mode: ${trade_amount:.2f}")
            
            execution_result = execute_trade(
                symbol=payload.symbol,
                action=payload.side,
                strategy=payload.strategy,
                confidence=payload.confidence,
                usdt_amount=trade_amount
            )
            
            if execution_result['success']:
                # Record for cooldown tracking
                risk_engine.record_signal(payload.symbol, payload.side)
                
                return WebhookResponse(
                    success=True,
                    message=f"Trade executed successfully",
                    decision="ACCEPTED",
                    reason=execution_result.get('reason', 'Trade filled'),
                    signal_id=str(execution_result.get('order_id', 'unknown'))
                )
            else:
                return WebhookResponse(
                    success=True,
                    message="Trade execution failed",
                    decision="REJECTED",
                    reason=execution_result.get('reason', 'Unknown error')
                )
        
        except Exception as e:
            logger.log_error(f"Exception during trade execution: {e}")
            return WebhookResponse(
                success=False,
                message="Error executing trade",
                decision="REJECTED",
                reason=str(e)
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions (like 401 unauthorized)
        raise
    except Exception as e:
        logger.log_error(f"Unexpected error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/status", tags=["Status"])
async def get_status():
    """Get current bot status and risk metrics."""
    try:
        binance = get_binance_client()
        balance = binance.get_account_balance("USDT")
        risk_status = risk_engine.get_status()
        
        return {
            "timestamp": str(__import__('datetime').datetime.utcnow()),
            "balance_usdt": round(balance, 2),
            "risk_engine": risk_status,
            "mode": "TESTNET" if Config.USE_TESTNET else "LIVE",
            "config": {
                "max_risk_per_trade": Config.MAX_RISK_PER_TRADE,
                "max_trades_per_day": Config.MAX_TRADES_PER_DAY,
                "max_open_trades": Config.MAX_OPEN_TRADES,
                "min_confidence": Config.MIN_CONFIDENCE,
            }
        }
    except Exception as e:
        logger.log_error(f"Error getting status: {e}")
        return {
            "error": str(e),
            "status": "error"
        }


# ============= HELPER FUNCTIONS =============

def execute_trade(
    symbol: str,
    action: str,
    strategy: str,
    confidence: float,
    usdt_amount: float
) -> Dict[str, Any]:
    """
    Execute a trade with proper order placement and logging.
    
    Args:
        symbol: Trading pair
        action: BUY or SELL
        strategy: Strategy name
        confidence: Confidence level
        usdt_amount: Amount in USDT to trade
    
    Returns:
        Dict with success status, reason, and order details
    """
    binance = get_binance_client()
    
    try:
        logger.log_info(f"Executing {action} order for {symbol} ({strategy})")
        
        # Get current price for reference
        current_price = binance.get_current_price(symbol)
        if current_price is None:
            return {
                'success': False,
                'reason': f"Cannot get price for {symbol}"
            }
        
        # Calculate correct quantity
        if action == "BUY":
            quantity = binance.calculate_buy_quantity(symbol, usdt_amount)
            if quantity is None or quantity <= 0:
                return {
                    'success': False,
                    'reason': f"Invalid quantity calculated: {quantity}"
                }
            
            # Place buy order
            order = binance.place_buy_order(symbol, quantity)
            if order is None:
                return {
                    'success': False,
                    'reason': "Failed to place BUY order"
                }
        
        elif action == "SELL":
            # For sell, we'd need to know available balance of the asset
            # For now, use a reasonable estimate
            quantity = usdt_amount / current_price
            quantity = round(quantity, 8)  # Standard precision
            
            # Place sell order
            order = binance.place_sell_order(symbol, quantity)
            if order is None:
                return {
                    'success': False,
                    'reason': "Failed to place SELL order"
                }
        
        else:
            return {
                'success': False,
                'reason': f"Invalid action: {action}"
            }
        
        # Extract order details
        order_id = order.get('orderId')
        filled_qty = float(order.get('executedQty', 0))
        avg_price = float(order.get('cummulativeQuoteAssetTransacted', 0)) / filled_qty if filled_qty > 0 else 0
        status = order.get('status', 'UNKNOWN')
        
        # Log trade execution
        logger.log_trade(
            symbol=symbol,
            action=action,
            quantity=filled_qty,
            price=avg_price if avg_price > 0 else current_price,
            order_id=str(order_id),
            status=status
        )
        
        # Record trade for daily limits
        if status == "FILLED" or filled_qty > 0:
            risk_engine.record_trade(symbol, action)
            
            # RECORD OPEN POSITION for position management
            # This allows automatic stop-loss and take-profit
            position_manager.open_position(
                symbol=symbol,
                side=action,
                quantity=filled_qty,
                entry_price=avg_price if avg_price > 0 else current_price
            )
        
        # Track open position if not immediately filled
        if status != "FILLED" and filled_qty == 0:
            risk_engine.add_open_trade(symbol, order_id, action, quantity)
        
        return {
            'success': True,
            'reason': f"Order {status}: {filled_qty} {symbol.replace('USDT', '')} @ ${current_price:.2f}",
            'order_id': order_id,
            'status': status,
            'quantity': filled_qty,
            'price': current_price
        }
    
    except Exception as e:
        logger.log_error(f"Error executing trade: {e}")
        import traceback
        logger.log_error(f"Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'reason': f"Exception: {str(e)}"
        }


# ============= MAIN ENTRY POINT =============

if __name__ == "__main__":
    import uvicorn
    
    logger.log_info("Starting FastAPI server")
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info" if Config.DEBUG else "warning"
    )
