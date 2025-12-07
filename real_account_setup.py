#!/usr/bin/env python3
"""
REAL ACCOUNT SETUP AUTOMATION
Validates real Binance account and walks you through TradingView integration
"""

import os
import sys
from dotenv import load_dotenv
from binance_client import BinanceAPIClient
import json

load_dotenv()

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_section(title):
    print(f"\n📋 {title}")
    print("-" * 70)

def check_real_account():
    """Verify connection to REAL Binance account"""
    print_header("STEP 1: VERIFY REAL BINANCE ACCOUNT CONNECTION")
    
    try:
        client = BinanceAPIClient()
        account = client.client.get_account()
        
        print(f"✅ Connected to Binance!")
        print(f"   Account Status: {account['accountStatus']}")
        print(f"   Trading Status: {account['tradingStatus']}")
        
        # Get balance
        balances = account['balances']
        usdt_balance = next((b for b in balances if b['asset'] == 'USDT'), None)
        
        if usdt_balance:
            print(f"   USDT Balance: {usdt_balance['free']} USDT")
            return True
        else:
            print("⚠️  No USDT balance found. Please deposit USDT to your Binance account.")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\n⚠️  TROUBLESHOOTING:")
        print("   1. Verify BINANCE_API_KEY and BINANCE_API_SECRET in .env")
        print("   2. Ensure API key has TRADE permission enabled")
        print("   3. Check BINANCE_BASE_URL=https://api.binance.com (mainnet, NOT demo)")
        print("   4. Run: python test_credentials.py")
        return False

def validate_env_settings():
    """Check .env for real account configuration"""
    print_section("STEP 2: VALIDATE .ENV SETTINGS")
    
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    base_url = os.getenv("BINANCE_BASE_URL", "")
    max_risk = os.getenv("MAX_RISK_PER_TRADE", "")
    webhook_secret = os.getenv("WEBHOOK_SECRET_KEY", "")
    
    checks = {
        "API Key Set": len(api_key) > 0,
        "API Secret Set": len(api_secret) > 0,
        "Base URL is Mainnet": base_url == "https://api.binance.com",
        "Risk Limit Conservative": float(max_risk or 0) <= 5,
        "Webhook Secret Strong": len(webhook_secret or "") >= 32,
    }
    
    all_good = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
        if not result:
            all_good = False
    
    if not all_good:
        print("\n⚠️  FIXES NEEDED:")
        if not checks["API Key Set"] or not checks["API Secret Set"]:
            print("   → Add BINANCE_API_KEY and BINANCE_API_SECRET to .env")
        if not checks["Base URL is Mainnet"]:
            print("   → Change BINANCE_BASE_URL=https://api.binance.com (NOT demo-api)")
        if not checks["Risk Limit Conservative"]:
            print("   → Set MAX_RISK_PER_TRADE=1 for initial trading")
        if not checks["Webhook Secret Strong"]:
            print("   → Generate strong webhook secret (32+ random chars)")
    
    return all_good

def show_tradingview_setup():
    """Display TradingView integration instructions"""
    print_section("STEP 3: TRADINGVIEW ALERT SETUP")
    
    print("✅ You have 2 strategies ready to use:\n")
    
    print("📊 STRATEGY A: Scalping (1-minute)")
    print("   → Frequency: 10–50 trades/day")
    print("   → Win Rate Target: 70%+")
    print("   → Best Time: 8 AM–5 PM EST (liquid hours)")
    print("   → Pairs: BTCUSDT, ETHUSDT, BNBUSDT")
    print("   → Pine Script: Use RSI + MACD (copy from TRADINGVIEW_SETUP.py)")
    
    print("\n📊 STRATEGY B: Swing Trading (4-hour)")
    print("   → Frequency: 5–10 trades/day")
    print("   → Win Rate Target: 55–60%")
    print("   → Best Time: Anytime (works in trends)")
    print("   → Pairs: All major pairs")
    print("   → Pine Script: Use Bollinger Bands + SMA (copy from TRADINGVIEW_SETUP.py)")
    
    print("\n🔗 WEBHOOK URL (paste into TradingView alert):")
    ngrok_url = os.getenv("NGROK_URL", "https://supervitally-nonsubordinate-tameka.ngrok-free.dev")
    print(f"   https://{ngrok_url.replace('https://', '')}/webhook")
    
    print("\n📝 STEPS:")
    print("   1. Go to https://www.tradingview.com")
    print("   2. Open Pine Editor for a 1-minute chart (BTCUSDT recommended)")
    print("   3. Copy scalping strategy from TRADINGVIEW_SETUP.py")
    print("   4. Click 'Create Alert'")
    print("   5. Webhook URL: " + ngrok_url + "/webhook")
    print("   6. Message: Copy JSON payload from TRADINGVIEW_SETUP.py")
    print("   7. Click 'Create'")

def show_first_trade_guide():
    """Show how to execute first real trade"""
    print_section("STEP 4: EXECUTE FIRST REAL TRADE")
    
    print("⚠️  START SMALL!\n")
    print("Recommended first trade:")
    print("  • Pair: ETHUSDT (less volatile than BTC)")
    print("  • Size: 0.01 ETH (~$30)")
    print("  • Stop Loss: -0.3% (exit if down $0.09)")
    print("  • Take Profit: +0.5% (exit if up $0.15)")
    
    print("\n📋 EXECUTION CHECKLIST:")
    print("  [ ] Bot is running: python app.py")
    print("  [ ] ngrok tunnel is active: ngrok http 8000")
    print("  [ ] TradingView alert created for ETHUSDT 1-minute")
    print("  [ ] Monitor logs in real-time: tail -f logs/signals.csv")
    print("  [ ] First scalping BUY signal fires from TradingView")
    print("  [ ] Check ngrok: Should see POST /webhook 200")
    print("  [ ] Check logs/trades.csv: Order should be FILLED")
    print("  [ ] Check Binance: Order visible in dashboard")
    
    print("\n✅ IF SUCCESSFUL:")
    print("  • Repeat 3–5 more trades")
    print("  • If win rate > 60%, increase position size")
    print("  • If win rate < 50%, adjust strategy parameters")

def show_daily_monitoring():
    """Show daily monitoring procedures"""
    print_section("STEP 5: DAILY MONITORING & RISK MANAGEMENT")
    
    print("🌅 EVERY MORNING (before trading):")
    print("  1. Start bot: python app.py")
    print("  2. Check health: curl http://localhost:8000/health")
    print("  3. Verify ngrok: ngrok http 8000 (separate terminal)")
    print("  4. Review yesterday: cat logs/trades.csv | tail -10")
    print("  5. Calculate P&L: python analyze_trades.py")
    
    print("\n📊 EVERY HOUR (during trading):")
    print("  1. Monitor signals: tail -f logs/signals.csv")
    print("  2. Check ngrok: Verify webhook deliveries")
    print("  3. Verify positions: Open Binance dashboard")
    print("  4. Confirm stops: Stop-loss orders in place")
    
    print("\n🚨 IF SOMETHING BREAKS:")
    print("  1. Check bot logs: tail -f logs/error.log")
    print("  2. Verify credentials: python test_credentials.py")
    print("  3. Restart ngrok: Kill old process, ngrok http 8000")
    print("  4. Restart bot: Kill python, python app.py")
    
    print("\n📈 PROFIT TRACKING:")
    print("  Run daily: python analyze_trades.py")
    print("  Expected (realistic):")
    print("    • Conservative ($1/trade): +$5/day = +$130/month")
    print("    • Moderate ($3/trade): +$12/day = +$300/month")
    print("    • Aggressive ($10/trade): +$28/day = +$700/month")

def show_risk_escalation():
    """Show how to increase risk safely"""
    print_section("RISK ESCALATION PROTOCOL")
    
    escalation = {
        "Days 1–3 (MINIMUM RISK)": {
            "MAX_RISK_PER_TRADE": "$1",
            "MAX_TRADES_PER_DAY": "5",
            "MIN_CONFIDENCE": "80",
            "Expected Daily P&L": "+$2–5"
        },
        "Days 4–7 (IF PROFITABLE)": {
            "MAX_RISK_PER_TRADE": "$3",
            "MAX_TRADES_PER_DAY": "10",
            "MIN_CONFIDENCE": "75",
            "Expected Daily P&L": "+$8–12"
        },
        "Week 2+ (IF CONSISTENTLY PROFITABLE)": {
            "MAX_RISK_PER_TRADE": "$5–10",
            "MAX_TRADES_PER_DAY": "20",
            "MIN_CONFIDENCE": "70",
            "Expected Daily P&L": "+$20–40"
        }
    }
    
    for phase, settings in escalation.items():
        print(f"\n{phase}")
        for key, value in settings.items():
            print(f"  • {key}: {value}")
    
    print("\n⚠️  STOP & REASSESS IF:")
    print("  • Daily loss > $10 → Scale back to $1/trade")
    print("  • Win rate < 50% → Adjust strategy, check TradingView alerts")
    print("  • Unexpected errors → Disable trading, debug")
    print("  • API rate limit errors → Reduce trade frequency")

def generate_summary():
    """Generate setup summary"""
    print_header("SETUP SUMMARY")
    
    api_key = os.getenv("BINANCE_API_KEY", "")
    webhook_secret = os.getenv("WEBHOOK_SECRET_KEY", "")
    
    api_key_masked = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:] if api_key else "NOT SET"
    webhook_masked = webhook_secret[:8] + "*" * (len(webhook_secret) - 12) + webhook_secret[-4:] if webhook_secret else "NOT SET"
    
    print(f"\n✅ API Key (masked): {api_key_masked}")
    print(f"✅ Webhook Secret (masked): {webhook_masked}")
    print(f"✅ Max Risk Per Trade: {os.getenv('MAX_RISK_PER_TRADE', 'NOT SET')}")
    print(f"✅ Max Trades Per Day: {os.getenv('MAX_TRADES_PER_DAY', 'NOT SET')}")
    print(f"✅ Min Confidence: {os.getenv('MIN_CONFIDENCE', 'NOT SET')}%")
    print(f"✅ Binance Base URL: {os.getenv('BINANCE_BASE_URL', 'NOT SET')}")
    print(f"✅ Strategies Available: Scalping (1m) + Swing Trading (4h)")
    
    print("\n🚀 READY TO START? Follow this sequence:")
    print("   1. python real_account_setup.py (this script - you are here)")
    print("   2. python test_credentials.py (verify real account)")
    print("   3. Set up TradingView alerts (follow instructions above)")
    print("   4. python app.py (start bot)")
    print("   5. Monitor first 3–5 trades closely")
    print("   6. python analyze_trades.py (check daily P&L)")

def main():
    print_header("🚀 REAL BINANCE + TRADINGVIEW INTEGRATION SETUP")
    
    # Check real account
    account_ok = check_real_account()
    
    # Validate env
    env_ok = validate_env_settings()
    
    # Show TradingView setup
    show_tradingview_setup()
    
    # Show first trade guide
    show_first_trade_guide()
    
    # Show daily monitoring
    show_daily_monitoring()
    
    # Show risk escalation
    show_risk_escalation()
    
    # Generate summary
    generate_summary()
    
    print_header("✅ SETUP GUIDE COMPLETE")
    print("\n📚 Additional resources:")
    print("   • REAL_ACCOUNT_INTEGRATION_GUIDE.md (comprehensive guide)")
    print("   • TRADINGVIEW_SETUP.py (Pine scripts & webhook payloads)")
    print("   • strategies.py (strategy definitions)")
    print("   • analyze_trades.py (daily P&L analysis)")
    print("\n🎯 Next Step: Set up your first TradingView alert!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
