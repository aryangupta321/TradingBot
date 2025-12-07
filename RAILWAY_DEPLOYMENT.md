# Railway Deployment Guide

This guide walks you through deploying the trading bot to Railway.

## What is Railway?

Railway.app is a simple cloud platform that:
- ✅ Runs your Python apps 24/7
- ✅ Has free tier (perfect for starting)
- ✅ Handles environment variables securely
- ✅ Auto-restarts on failures
- ✅ Easy to scale when needed

## Step 1: Prepare Your Code

Ensure your project is clean:

```bash
# Verify all files exist
Trading/
├── app.py
├── config.py
├── csv_logger.py
├── risk.py
├── binance_client.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
└── logs/
    └── .gitkeep
```

## Step 2: Create .gitignore (Important!)

Make sure `.gitignore` includes `.env` so secrets aren't committed:

```
.env
.env.local
venv/
__pycache__/
*.pyc
logs/*.csv
```

## Step 3: Push to GitHub

```bash
cd Trading

# Initialize git repo if not already done
git init
git add -A
git commit -m "Initial commit: trading bot"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/trading-bot.git
git branch -M main
git push -u origin main
```

## Step 4: Create Railway Account

1. Go to https://railway.app
2. Click "Start Project"
3. Sign up with GitHub (recommended - easier integration)
4. Authorize Railway to access your GitHub

## Step 5: Deploy from GitHub

1. In Railway, click "+ New"
2. Select "Deploy from GitHub"
3. Select your `trading-bot` repository
4. Railway will auto-detect it's a Python project
5. Click "Deploy" (it'll fail initially without env vars)

## Step 6: Configure Environment Variables

**CRITICAL**: Set these before the bot runs:

1. In Railway, go to your project settings
2. Click "Variables" tab
3. Add these variables (copy from `.env.example`):

```
BINANCE_API_KEY=your_actual_api_key
BINANCE_API_SECRET=your_actual_api_secret
WEBHOOK_SECRET_KEY=your_random_secret_key_32_chars
USE_TESTNET=true
MAX_RISK_PER_TRADE=10
MAX_TRADES_PER_DAY=10
MAX_OPEN_TRADES=3
MIN_BALANCE_USDT=10
SIGNAL_COOLDOWN_SECONDS=300
MIN_CONFIDENCE=50
PORT=8000
HOST=0.0.0.0
```

**SECURITY**: 
- Never paste actual secrets into Railway UI - type them fresh
- Use different secrets for testnet vs live
- Keep testnet API key in separate account if possible

## Step 7: Configure Start Command

Railway needs to know how to start your app:

1. In your repo root, create `Procfile`:

```
web: python app.py
```

Or Railway may auto-detect. If deployment fails, add the Procfile above.

2. Commit and push:
```bash
git add Procfile
git commit -m "Add Procfile for Railway"
git push
```

## Step 8: Monitor Deployment

1. In Railway, go to "Deployments"
2. Wait for build to complete
3. Check logs for errors:
   - Click "View Logs"
   - Should see: `[INFO] Bot ready to receive signals`
4. Get your public URL:
   - Click "Settings"
   - Copy your Railway URL (e.g., `https://trading-bot-prod.up.railway.app`)

## Step 9: Test Webhook

```bash
# Replace with your actual Railway URL and secret
curl -X POST https://trading-bot-prod.up.railway.app/webhook \
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

Should return:
```json
{
  "success": true,
  "decision": "ACCEPTED",
  "reason": "All risk constraints satisfied"
}
```

## Step 10: Setup TradingView Webhook

In TradingView alert settings:

```
Webhook URL: https://trading-bot-prod.up.railway.app/webhook

Message:
{
  "symbol": "{{ticker}}",
  "side": "{{strategy.order.action}}",
  "strategy": "My Strategy",
  "timeframe": "{{interval}}",
  "confidence": 75,
  "secret": "your-secret-key"
}
```

Or use header auth (more secure):

```
Headers:
  Authorization: Bearer your-secret-key
  Content-Type: application/json

Message (without secret field):
{
  "symbol": "{{ticker}}",
  "side": "{{strategy.order.action}}",
  "strategy": "My Strategy",
  "timeframe": "{{interval}}",
  "confidence": 75
}
```

## Viewing Logs

### Real-time logs on Railway:

1. Go to Railway project
2. Click "View Logs"
3. Scroll to see all activity

### CSV logs:

Unfortunately, Railway's filesystem is ephemeral (resets on redeploy). To persist logs:

**Option A**: Download logs before redeploying
- SSH into Railway or use Railway CLI
- Download `logs/signals.csv` and `logs/trades.csv`

**Option B**: Add persistent volume (paid feature)
- In Railway settings, add persistent volume
- Costs ~$5/month for small size

**Option C**: Send logs to external service
- Add Telegram notifications
- Send logs to external database
- Cloud storage integration (S3, etc)

For now, check logs frequently:
```bash
# SSH into Railway (via CLI)
railway run bash

# View logs
cat logs/signals.csv
cat logs/trades.csv
```

## Common Issues

### "Port is already in use"
Railway assigns port dynamically. Make sure `PORT=8000` but Railway might use different port.

**Fix**: Update `config.py` to use Railway's `$PORT` env var:
```python
PORT = int(os.getenv("PORT", "8000"))
```

### "Binance credentials invalid"
Double-check your API keys in Railway environment variables. Copy-paste errors are common.

### "Build fails"
Check logs for missing dependencies. Make sure `requirements.txt` is up to date:
```bash
pip freeze > requirements.txt
```

### "Module not found"
Make sure all imports are in `requirements.txt`. Common issue: missing `python-binance`.

Verify:
```bash
pip install -r requirements.txt
python config.py
```

## Updating Your Bot

To deploy changes:

```bash
# Make your code changes
nano app.py  # or your editor

# Commit and push
git add -A
git commit -m "Update: add feature X"
git push

# Railway auto-redeploys
# Monitor in Railway dashboard
```

## Environment Variable Security

**DO NOT**:
- Paste secrets into public logs
- Share `.env` file with anyone
- Commit `.env` to git
- Use same secret for testnet and live

**DO**:
- Rotate secrets every 3 months
- Use unique API keys for each environment
- Restrict API key IP in Binance settings
- Monitor API usage in Binance dashboard
- Delete unused API keys

## Cost Estimation

Railway pricing (as of 2024):

- **Free tier**: 
  - $5/month free credit
  - OK for learning/testing
  - Ephemeral storage (logs lost on redeploy)

- **Paid**:
  - ~$5/month for persistent 1GB storage
  - Per-GB bandwidth charges
  - Usually < $10/month for light usage

For a simple trading bot, free tier usually works fine if you don't need persistent logs.

## Advanced: Database for Logs

For production, persist logs to database:

1. Add PostgreSQL plugin to Railway:
   - Click "+ Add"
   - Select "PostgreSQL"
   - Railway auto-provisions and provides connection string

2. Update `csv_logger.py` to write to database instead of CSV
3. Create simple API endpoint to query logs
4. Download/export as CSV when needed

## Monitoring & Alerts

1. **Status checks**: 
   ```bash
   # Check health
   curl https://your-app.railway.app/health
   ```

2. **Set up webhook monitoring**:
   - Use external monitoring service (Pingdom, UptimeRobot)
   - Send test signal daily to verify bot is responsive

3. **Railway alerts**:
   - In Railway settings, enable deployment failure notifications
   - Get email when bot crashes or fails to deploy

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Test with testnet signals
3. ✅ Monitor for 1-2 weeks
4. ✅ Review `signals.csv` and `trades.csv`
5. ✅ Switch to live trading if comfortable (change `USE_TESTNET=false`)
6. ✅ Keep checking logs regularly

## Support

- Railway docs: https://railway.app/docs
- Bot README: See README.md in project root
- Troubleshooting: Check Railway logs for specific errors

---

**Remember**: Start with testnet, test thoroughly, then go live with small amounts! 🚀
