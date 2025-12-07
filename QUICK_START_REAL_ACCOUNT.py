#!/usr/bin/env python3
"""
QUICK START: Switch from Demo to Real Binance Account
Copy-paste these exact changes into your .env file
"""

print("""
╔════════════════════════════════════════════════════════════════════════╗
║         SWITCH FROM DEMO TO REAL BINANCE ACCOUNT                      ║
║              Step-by-Step Configuration Changes                        ║
╚════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1: Get Real Binance API Key
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to: https://www.binance.com/en/my/settings/api-management
2. Click "Create API"
3. Name: TradingViewBot
4. RESTRICTIONS (CRITICAL - select ONLY these):
   ✅ Enable Spot & Margin Trading
   ❌ Everything else disabled
5. IP Whitelist: (optional) Enter your home IP
6. Confirm with SMS/Email
7. Copy API Key and Secret (save somewhere encrypted!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2: Update Your .env File
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current .env (DEMO Account):
────────────────────────────
BINANCE_API_KEY=your_demo_api_key_here
BINANCE_API_SECRET=your_demo_secret_here
USE_TESTNET=false
BINANCE_BASE_URL=https://demo-api.binance.com
MAX_RISK_PER_TRADE=10
MAX_TRADES_PER_DAY=10
MIN_CONFIDENCE=50
WEBHOOK_SECRET_KEY=change_this_to_a_random_secret_key_at_least_32_chars_long


🔄 CHANGE TO THIS (REAL Account - Conservative):
────────────────────────────────────────────────
BINANCE_API_KEY=your_real_api_key_here
BINANCE_API_SECRET=your_real_secret_here
USE_TESTNET=false
BINANCE_BASE_URL=https://api.binance.com              ← CHANGE: demo-api → api
MAX_RISK_PER_TRADE=1                                  ← CHANGE: 10 → 1 (START SMALL!)
MAX_TRADES_PER_DAY=5                                  ← CHANGE: 10 → 5
MIN_CONFIDENCE=75                                     ← CHANGE: 50 → 75
WEBHOOK_SECRET_KEY=your_new_random_secret_32_chars   ← Generate new secure key


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3: Critical Differences (DEMO vs REAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Configuration Item              | DEMO Account        | REAL Account
─────────────────────────────────────────────────────────────────────────────
BINANCE_BASE_URL               | demo-api.binance.com | api.binance.com
MAX_RISK_PER_TRADE             | $10 (testing)        | $1–5 (conservative)
MAX_TRADES_PER_DAY             | 10                   | 5–20 (scale gradually)
MIN_CONFIDENCE                 | 50% (lenient)        | 70–80% (strict)
API Key Permissions            | All                  | TRADE ONLY
Real Money at Risk             | NO ❌                | YES ⚠️
Profit/Loss                    | Virtual (fake P&L)  | Real dollars
Default Position Size          | $10–20 per trade    | $1–5 per trade


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4: Verify Real Account Connection (Test Before Trading)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run this command to verify:
  
  python test_credentials.py

Expected output:
  ✅ Testing credentials on https://api.binance.com
  ✅ API key valid on REAL MAINNET
  ✅ Account balance: 1000.50 USDT
  ✅ You are ready for real trading!


⚠️  If you see errors:
  ❌ "Invalid API-key" → Check API key/secret, verify TRADE permission
  ❌ "403 Forbidden" → IP whitelist issue, add your IP to Binance settings
  ❌ Connection refused → Check BINANCE_BASE_URL = https://api.binance.com


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5: Set Up TradingView Alerts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open https://www.tradingview.com
2. Choose a pair (BTCUSDT, ETHUSDT recommended)
3. Set timeframe to 1-minute (for scalping) or 4-hour (for swing)
4. Open Pine Editor (bottom left)
5. Copy-paste ONE strategy:
   📌 SCALPING (1-minute, high-frequency)
      From: TRADINGVIEW_SETUP.py → Copy "Scalping RSI+MACD [High Win Rate]"
   
   📌 SWING TRADING (4-hour, trending markets)
      From: TRADINGVIEW_SETUP.py → Copy "Swing Bollinger Bands + Moving Averages"

6. Click "Create Alert"
7. Configure alert:
   • Condition: (your strategy's buy/sell signal)
   • Webhook URL: https://supervitally-nonsubordinate-tameka.ngrok-free.dev/webhook
   • Message: (copy JSON from TRADINGVIEW_SETUP.py)
8. Test: Wait for first signal and monitor logs/signals.csv


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 6: Start Real Trading (Step-by-Step)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Terminal 1 - Start Bot:
  > python app.py
  Output: "Bot ready to receive signals"

Terminal 2 - Expose Webhook:
  > ngrok http 8000
  Output: "Forwarding https://supervitally-nonsubordinate-tameka.ngrok-free.dev"

Terminal 3 - Monitor Trades:
  > tail -f logs/signals.csv
  Output: (watch signals in real-time)

Wait for first TradingView signal → Bot executes trade → Check Binance dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 7: Risk Escalation Schedule
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 DAYS 1–3 (MINIMUM RISK - Validate Strategy)
   • MAX_RISK_PER_TRADE=1 ($1 per trade)
   • MAX_TRADES_PER_DAY=5
   • MIN_CONFIDENCE=80
   • Goal: Execute 5–15 trades, hit 60%+ win rate
   • Expected P&L: +$2–5/day


📅 DAYS 4–7 (SCALE UP - If Profitable)
   • MAX_RISK_PER_TRADE=3 ($3 per trade)
   • MAX_TRADES_PER_DAY=10
   • MIN_CONFIDENCE=75
   • Goal: Consistent profitability, refine strategy
   • Expected P&L: +$8–15/day


📅 WEEK 2+ (OPTIMIZE - If Win Rate > 55%)
   • MAX_RISK_PER_TRADE=5–10 ($5–10 per trade)
   • MAX_TRADES_PER_DAY=20
   • MIN_CONFIDENCE=70
   • Goal: Maximize profit, expand to multiple strategies
   • Expected P&L: +$25–60/day


⛔ STOP & REASSESS IF:
   • Daily loss > $10 → Reduce to MAX_RISK_PER_TRADE=1
   • Win rate < 50% → Pause trading, review strategy
   • 3 consecutive losses → Stop trading for the day
   • Unexpected errors → Disable trading, debug


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAILY CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌅 EVERY MORNING:
  [ ] Bot running: python app.py
  [ ] ngrok active: ngrok http 8000
  [ ] Health check: curl http://localhost:8000/health
  [ ] View yesterday's P&L: python analyze_trades.py
  [ ] Check Binance balance: Confirm available USDT

📊 EVERY HOUR (during trading):
  [ ] Monitor signals: tail -f logs/signals.csv
  [ ] Watch ngrok: Verify webhook requests
  [ ] Check Binance: Verify open positions
  [ ] Confirm stops: Stop-loss orders active

🌙 EVERY EVENING:
  [ ] Review daily P&L: python analyze_trades.py
  [ ] Analyze trades: cat logs/trades.csv | tail -20
  [ ] Plan tomorrow: Adjust if needed based on performance
  [ ] Backup logs: Keep records of all trades


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXPECTED RETURNS (REALISTIC ESTIMATES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Conservative Strategy ($1/trade, 20 trades/day, 70% win rate):
  • Average Win: $0.50
  • Average Loss: ($0.30)
  • Daily P&L: $5.20
  • Monthly: $130 (20 trading days)
  • Yearly: $1,560

Moderate Strategy ($3/trade, 15 trades/day, 65% win rate):
  • Average Win: $2.00
  • Average Loss: ($1.50)
  • Daily P&L: $11.62
  • Monthly: $290 (25 trading days)
  • Yearly: $3,480

Aggressive Strategy ($10/trade, 10 trades/day, 60% win rate):
  • Average Win: $8.00
  • Average Loss: ($5.00)
  • Daily P&L: $28
  • Monthly: $700 (25 trading days)
  • Yearly: $8,400

⚠️  NOTE: These are estimates. Actual results depend on:
   • Market conditions (bull, bear, consolidation)
   • Strategy signal quality (TradingView alert accuracy)
   • Execution speed (slippage, order fills)
   • Risk management discipline (following rules)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ "Invalid API-key / Unable to connect"
   ✅ Solution: 
      1. Run: python test_credentials.py
      2. Verify BINANCE_API_KEY and BINANCE_API_SECRET in .env
      3. Check BINANCE_BASE_URL=https://api.binance.com (not demo-api!)
      4. Wait 5 min after API key creation (Binance delays sometimes)

❌ "Webhook returns 401 Unauthorized"
   ✅ Solution:
      1. Verify WEBHOOK_SECRET_KEY matches in .env
      2. Check ngrok URL is https (never http)
      3. Verify JSON payload has correct format

❌ "No trades executing despite alerts firing"
   ✅ Solution:
      1. Check MIN_CONFIDENCE setting (signal confidence < MIN_CONFIDENCE will be rejected)
      2. Verify ngrok tunnel is active
      3. Check logs/signals.csv for decision reason
      4. Increase confidence in TradingView alert if being rejected

❌ "Trades execute but stop-loss not triggering"
   ✅ Solution:
      1. Verify stop-loss order was placed (check logs/trades.csv)
      2. Check Binance dashboard for open orders
      3. Ensure position is large enough for stop-loss percentage

❌ "Account balance not updating"
   ✅ Solution:
      1. Check Binance API hasn't hit rate limit
      2. Verify TRADE permission is enabled on API key
      3. Manual check: https://www.binance.com/en/account/my-btc


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 📋 Create real Binance API key (https://www.binance.com/en/my/settings/api-management)
2. 📝 Update .env with real credentials and conservative risk limits
3. ✅ Run: python test_credentials.py (verify real account works)
4. 🎯 Set up TradingView alerts (copy Pine scripts from TRADINGVIEW_SETUP.py)
5. 🤖 Start bot: python app.py
6. 🌐 Enable ngrok: ngrok http 8000
7. 📊 Monitor first trades closely
8. 📈 Scale up gradually based on win rate

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  DISCLAIMER: Trading real money involves financial risk. Past performance 
    does not guarantee future results. Start with minimum position sizes. 
    Never risk money you can't afford to lose.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
