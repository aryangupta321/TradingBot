# QUICK START GUIDE

Get your trading bot running in 5 minutes! 🚀

## Prerequisites

- Python 3.8+ installed
- Binance account (free)
- TradingView account (free)

## 1. Setup (2 minutes)

```bash
# Navigate to project
cd Trading

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure (2 minutes)

```bash
# Copy example config
cp .env.example .env

# Edit .env with your values
# Edit with your favorite editor (VS Code, nano, etc)
```

**In .env, MUST SET:**
```
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
WEBHOOK_SECRET_KEY=pick_a_random_secret_key
USE_TESTNET=true
```

**Get Binance API Key:**
1. Go to https://www.binance.com
2. Log in
3. Settings → API Management
4. Create new API key
5. Copy Key and Secret into .env

## 3. Validate Setup (1 minute)

```bash
# Run validation test
python test_setup.py
```

Should show: ✓ ALL CHECKS PASSED

## 4. Start Bot! (under 1 minute)

```bash
# Start the bot
python app.py
```

You should see:
```
[INFO ...] TRADING BOT STARTING UP
[INFO ...] Account USDT Balance: $X.XX
[INFO ...] Bot ready to receive signals
```

The bot is now listening at `http://localhost:8000`

## 5. Test It Works

In another terminal:

```bash
# Test webhook (replace secret with yours)
curl -X POST http://localhost:8000/webhook \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "strategy": "Test",
    "timeframe": "4h",
    "confidence": 75
  }'
```

You should get back:
```json
{
  "success": true,
  "decision": "ACCEPTED",
  "reason": "All risk constraints satisfied"
}
```

Check the logs:
```bash
# View signals
cat logs/signals.csv

# View trades (if executed)
cat logs/trades.csv
```

## 6. API Documentation

Visit `http://localhost:8000/docs` in your browser for interactive API docs.

## Common Next Steps

**Stop the bot:**
```
Ctrl+C in the terminal
```

**Check bot status:**
```bash
curl http://localhost:8000/status | python -m json.tool
curl http://localhost:8000/health | python -m json.tool
```

**View logs:**
```bash
# Real-time signal log
tail -f logs/signals.csv

# Real-time trade log
tail -f logs/trades.csv
```

**Deploy to Railway (cloud):**
See `RAILWAY_DEPLOYMENT.md`

**Troubleshooting:**
See `README.md` FAQ section

## Key Configuration Options

Edit `.env` to customize:

```
MAX_RISK_PER_TRADE=10              # Max $10 per trade
MAX_TRADES_PER_DAY=10              # Max 10 trades/day
MIN_CONFIDENCE=50                  # Reject signals < 50% confidence
SIGNAL_COOLDOWN_SECONDS=300        # Prevent same signal spam
USE_TESTNET=true                   # Use fake money (testnet)
```

## Security Checklist

- [ ] Changed WEBHOOK_SECRET_KEY to something unique
- [ ] API key has IP whitelist in Binance settings
- [ ] Withdrawals DISABLED for API key in Binance
- [ ] .env is NOT committed to git (check .gitignore)
- [ ] Using TESTNET=true initially
- [ ] Starting with small amounts ($1-10 per trade)

## 🎓 Learning Path

1. **Day 1-2**: Run on testnet, send test signals
2. **Day 3-7**: Run for week, review signals.csv for accuracy
3. **Week 2**: If confident, switch to LIVE (change USE_TESTNET=false)
4. **Week 2+**: Monitor trade results, adjust settings as needed

## 📚 Full Documentation

- **README.md** - Complete guide with all features
- **RAILWAY_DEPLOYMENT.md** - Cloud deployment
- **API Docs** - http://localhost:8000/docs (when running)

## 🆘 Still Having Issues?

1. Check bot logs for error messages
2. Run `python test_setup.py` to validate setup
3. Review README.md "Troubleshooting" section
4. Verify .env has real Binance API keys (not example)
5. Check internet connection to Binance API

## 🚀 You're Ready!

Your bot is configured and running. Now:

1. Setup TradingView alerts (see README.md)
2. Send test signal
3. Review logs
4. Go live when ready!

---

**Remember:** Testnet first! Small amounts! Trade safely! 💡
