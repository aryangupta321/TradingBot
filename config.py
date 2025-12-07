"""
Configuration module - loads environment variables with sensible defaults.
This is the single source of truth for all bot configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """Central configuration class for the trading bot."""
    
    # ============= API KEYS & SECURITY =============
    # Binance API credentials
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
    
    # Webhook security - secret key for validating incoming alerts
    WEBHOOK_SECRET_KEY = os.getenv("WEBHOOK_SECRET_KEY", "your-super-secret-key-change-in-production")
    
    # ============= BINANCE SETTINGS =============
    # Use testnet for safer trading during development
    USE_TESTNET = os.getenv("USE_TESTNET", "true").lower() == "true"
    
    # Testnet API endpoints
    BINANCE_TESTNET_API = "https://testnet.binance.vision"
    BINANCE_TESTNET_WS = "wss://stream.testnet.binance.vision"
    
    # Live API endpoints
    BINANCE_LIVE_API = "https://api.binance.com"
    BINANCE_LIVE_WS = "wss://stream.binance.com"
    
    # Optional override for Binance API base URL (useful for demo/proxy endpoints)
    BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "")
    
    # ============= RISK MANAGEMENT =============
    # Auto-reinvestment mode: use percentage of balance instead of fixed amount
    USE_PERCENTAGE_RISK = os.getenv("USE_PERCENTAGE_RISK", "true").lower() == "true"
    
    # Percentage of balance to risk per trade (0.0 to 1.0)
    # Example: 0.50 = 50% of balance per trade (aggressive compounding)
    RISK_PERCENTAGE = float(os.getenv("RISK_PERCENTAGE", "0.50"))
    
    # Maximum USDT risk per single trade (in USDT) - used if USE_PERCENTAGE_RISK=false
    MAX_RISK_PER_TRADE = float(os.getenv("MAX_RISK_PER_TRADE", "10"))
    
    # Maximum number of simultaneous open trades
    MAX_OPEN_TRADES = int(os.getenv("MAX_OPEN_TRADES", "3"))
    
    # Maximum trades per day
    MAX_TRADES_PER_DAY = int(os.getenv("MAX_TRADES_PER_DAY", "10"))
    
    # Minimum account balance in USDT to allow trading
    MIN_BALANCE_USDT = float(os.getenv("MIN_BALANCE_USDT", "10"))
    
    # Cooldown period between duplicate signals (in seconds)
    SIGNAL_COOLDOWN_SECONDS = int(os.getenv("SIGNAL_COOLDOWN_SECONDS", "300"))
    
    # Minimum confidence level (0-100) to execute a trade
    MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "50"))
    
    # ============= SERVER SETTINGS =============
    # FastAPI server host and port
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Enable debug mode (NOT for production)
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # ============= NOTIFICATIONS =============
    # Telegram bot token and chat ID (optional)
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # ============= LOGGING =============
    # CSV log file paths
    LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
    SIGNALS_CSV = LOG_DIR / "signals.csv"
    TRADES_CSV = LOG_DIR / "trades.csv"
    
    # Ensure log directory exists
    LOG_DIR.mkdir(exist_ok=True)


# Validate critical configuration on startup
def validate_config():
    """Validate that critical configuration values are properly set."""
    if not Config.BINANCE_API_KEY or not Config.BINANCE_API_SECRET:
        raise ValueError(
            "ERROR: BINANCE_API_KEY and BINANCE_API_SECRET must be set in .env file\n"
            "See .env.example for format"
        )
    
    if Config.WEBHOOK_SECRET_KEY == "your-super-secret-key-change-in-production":
        raise ValueError(
            "ERROR: WEBHOOK_SECRET_KEY has default value! "
            "Change it in .env file for security"
        )
    
    if Config.MAX_RISK_PER_TRADE <= 0:
        raise ValueError("MAX_RISK_PER_TRADE must be positive")
    
    if Config.RISK_PERCENTAGE <= 0 or Config.RISK_PERCENTAGE > 1.0:
        raise ValueError("RISK_PERCENTAGE must be between 0.0 and 1.0")
    
    if Config.MAX_OPEN_TRADES < 1:
        raise ValueError("MAX_OPEN_TRADES must be at least 1")



if __name__ == "__main__":
    # Quick validation when run directly
    try:
        validate_config()
        print("✓ Configuration validated successfully")
        print(f"  Testnet mode: {Config.USE_TESTNET}")
        print(f"  Max risk per trade: ${Config.MAX_RISK_PER_TRADE}")
        print(f"  Max trades per day: {Config.MAX_TRADES_PER_DAY}")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
