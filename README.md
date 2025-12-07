# Crypto Trading Bot

A production-ready, minimal trading bot that receives TradingView webhook signals and executes trades on Binance testnet/live.

**⚠️ IMPORTANT DISCLAIMER:** This bot does NOT guarantee profits. Cryptocurrency trading is highly risky. Start with testnet, use small position sizes, and understand that you can lose your entire investment. Only trade with money you can afford to lose.

## Features

- ✅ **Security-First**: Webhook secret key validation, no hardcoded credentials
- ✅ **Risk Control**: Max risk per trade, daily trade limits, duplicate signal cooldown, minimum balance checks
- ✅ **Production Code**: Proper error handling, logging, configuration management
- ✅ **Testnet First**: Start safely with Binance testnet before trading real money
- ✅ **CSV Logging**: Human-readable logs for Excel analysis
- ✅ **FastAPI**: Modern async webhook server with auto-documentation
- ✅ **Easy Deployment**: Railway-compatible, single Python 3 dependency list
- ✅ **Beginner-Friendly**: Clean, commented code with examples

## Project Structure

```
Trading/
├── app.py                 # Main FastAPI webhook server
├── config.py              # Configuration & environment variables
├── csv_logger.py          # CSV logging for signals and trades
├── risk.py                # Risk management engine
├── binance_client.py      # Binance API wrapper with error handling
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── logs/                  # CSV logs directory (auto-created)
│   ├── signals.csv       # All received signals and decisions
│   └── trades.csv        # Executed trades
└── README.md             # This file
```

## Installation

### 1. Clone & Setup

```bash
# Clone the repository
cd Trading

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Binance API Keys

1. Create Binance account: https://www.binance.com
2. Go to Settings → API Management
3. Create new API key with these permissions:
   - ✅ Enable Spot & Margin Trading
   - ✅ Enable Reading Account Trade History
   - ⚠️ Disable Withdrawals (for security)
4. Save your API Key and Secret Key

### 3. Setup Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your values
# See .env.example for all options
```

**Required Variables:**
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
WEBHOOK_SECRET_KEY=change_this_to_random_secret
USE_TESTNET=true
```

### 4. Test Connection

```bash
python config.py
```

You should see: `✓ Configuration validated successfully`

## Quick Start

### 1. Start the Bot

```bash
python app.py
```

You should see:
```
[INFO ...] TRADING BOT STARTING UP
[INFO ...] Account USDT Balance: $100.00
[INFO ...] Bot ready to receive signals
```

The bot is now listening on `http://localhost:8000`

### 2. Send a Test Signal

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "strategy": "RSI Oversold",
    "timeframe": "4h",
    "confidence": 75
  }'
```

Or with secret in body:
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "strategy": "RSI Oversold",
    "timeframe": "4h",
    "confidence": 75,
    "secret": "your-secret-key"
  }'
```

### 3. Check Logs

```bash
# View signals (all received signals and decisions)
cat logs/signals.csv

# View trades (executed trades only)
cat logs/trades.csv
```

### 4. Monitor Bot Status

```bash
# Health check
curl http://localhost:8000/health

# Full status with risk limits
curl http://localhost:0000/status
```

### 5. API Documentation

Visit `http://localhost:8000/docs` for interactive API docs (Swagger UI)

## Configuration

All settings in `config.py` are controlled via environment variables. Key ones:

| Variable | Default | Description |
|----------|---------|-------------|
| `BINANCE_API_KEY` | *required* | Your Binance API key |
| `BINANCE_API_SECRET` | *required* | Your Binance API secret |
| `WEBHOOK_SECRET_KEY` | *required* | Secret for webhook validation |
| `USE_TESTNET` | `true` | Use testnet (true) or live trading (false) |
| `MAX_RISK_PER_TRADE` | `10` | Max USDT per trade |
| `MAX_TRADES_PER_DAY` | `10` | Max trades per day |
| `MAX_OPEN_TRADES` | `3` | Max simultaneous open positions |
| `MIN_BALANCE_USDT` | `10` | Minimum balance required to trade |
| `SIGNAL_COOLDOWN_SECONDS` | `300` | Min seconds between duplicate signals |
| `MIN_CONFIDENCE` | `50` | Minimum confidence level (0-100) |
| `PORT` | `8000` | Server port |
| `HOST` | `0.0.0.0` | Server host |

## TradingView Integration

### Setup Webhook in TradingView

1. In TradingView, create your strategy with alerts
2. Add alert action: **"Webhook URL"**
3. Enter webhook URL: `https://your-domain.com/webhook`
4. Message JSON:
```json
{
  "symbol": "{{ticker}}",
  "side": "{{strategy.order.action}}",
  "strategy": "My Strategy Name",
  "timeframe": "{{interval}}",
  "confidence": 75,
  "secret": "your-secret-key"
}
```

Or send secret in header (more secure):
- Header: `Authorization: Bearer your-secret-key`
- Message JSON (no secret field):
```json
{
  "symbol": "{{ticker}}",
  "side": "{{strategy.order.action}}",
  "strategy": "My Strategy Name",
  "timeframe": "{{interval}}",
  "confidence": 75
}
```

## Webhook Request Format

### POST /webhook

**Headers (choose one authentication method):**

Method 1 - Header:
```
Authorization: Bearer your-secret-key
Content-Type: application/json
```

Method 2 - Body:
```
Content-Type: application/json
```

**Body:**
```json
{
  "symbol": "BTCUSDT",      // Required: Trading pair
  "side": "BUY",             // Required: BUY or SELL
  "strategy": "RSI",         // Optional: Strategy name
  "timeframe": "4h",         // Optional: Timeframe
  "confidence": 75,          // Optional: 0-100 confidence
  "secret": "your-key"       // Optional if in header
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Trade executed successfully",
  "decision": "ACCEPTED",
  "reason": "All risk constraints satisfied",
  "signal_id": "12345"
}
```

**Response (Rejected by Risk Engine):**
```json
{
  "success": true,
  "message": "Signal received but rejected by risk engine",
  "decision": "REJECTED",
  "reason": "Daily trade limit 10 reached (10 executed today)"
}
```

## Risk Management

The bot implements multiple risk layers:

1. **Confidence Threshold**: Rejects signals below `MIN_CONFIDENCE`
2. **Minimum Balance**: Won't trade if balance < `MIN_BALANCE_USDT`
3. **Max Risk Per Trade**: Limits each trade to `MAX_RISK_PER_TRADE` USDT
4. **Daily Trade Limit**: Max `MAX_TRADES_PER_DAY` per day (resets at midnight UTC)
5. **Open Position Limit**: Max `MAX_OPEN_TRADES` simultaneous positions
6. **Duplicate Prevention**: Same signal within `SIGNAL_COOLDOWN_SECONDS` is rejected

All decisions are logged to `logs/signals.csv` with reasons.

## CSV Logs

### signals.csv
- DateTime: When signal was received
- TradingPair: Symbol (BTCUSDT, etc)
- Action: BUY or SELL
- Strategy: Strategy name from signal
- TimeFrame: Timeframe from signal
- Confidence: Confidence level
- Decision: ACCEPTED or REJECTED
- Reason: Why accepted/rejected

### trades.csv
- DateTime: When trade was executed
- TradingPair: Symbol
- Action: BUY or SELL
- TradeAmount: Total value in USDT
- Price: Execution price
- OrderID: Binance order ID
- Status: FILLED, PENDING, FAILED, etc

## Deployment

### Railway

Railway is a simple hosting platform (free for small apps):

1. Create account: https://railway.app
2. Connect your GitHub repository
3. Create new project from GitHub repo
4. Set environment variables:
   - `BINANCE_API_KEY`
   - `BINANCE_API_SECRET`
   - `WEBHOOK_SECRET_KEY`
   - `USE_TESTNET=true` (recommended initially)
   - Other config as needed
5. Deploy

Your webhook URL will be: `https://yourapp.railway.app/webhook`

### Local Development

```bash
# Activate venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start bot
python app.py

# Visit http://localhost:8000/docs for API docs
```

### Production Server (Linux)

```bash
# Install dependencies
pip install -r requirements.txt

# Run with gunicorn (production-grade)
pip install gunicorn

# Run on port 8000
gunicorn -w 1 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000

# Or with systemd (for persistence)
# See systemd service file example in docs/
```

## Error Handling

The bot implements comprehensive error handling:

- **Network errors**: Logged and alerts skipped
- **Invalid API keys**: Caught at startup
- **Insufficient balance**: Trade rejected, logged
- **Symbol not found**: Trade rejected with reason
- **Order placement fails**: Logged with Binance error
- **Invalid webhook format**: Returns 400 Bad Request
- **Missing secret key**: Returns 401 Unauthorized

All errors are logged to console with timestamp.

## Testing

### Test with Testnet

The bot defaults to Binance testnet (fake money):

```bash
# In .env:
USE_TESTNET=true
```

Testnet is perfect for:
- Testing your strategy without risk
- Debugging webhook integration
- Validating order placement logic
- Verifying logging

### Create Test Signal

```bash
# Using curl
curl -X POST http://localhost:8000/webhook \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "strategy": "Test Strategy",
    "timeframe": "4h",
    "confidence": 75
  }'

# Check logs
tail -f logs/signals.csv
tail -f logs/trades.csv
```

### Check Bot Status

```bash
curl http://localhost:8000/health | python -m json.tool
curl http://localhost:8000/status | python -m json.tool
```

## Security Best Practices

1. **Keep API keys secret**: Never commit `.env` to git
2. **Use testnet first**: Always test before live trading
3. **Use IP whitelist**: In Binance API management, restrict to your IP
4. **Rotate secret key**: Change `WEBHOOK_SECRET_KEY` periodically
5. **Monitor logs**: Check `signals.csv` and `trades.csv` regularly
6. **Limit permissions**: Disable withdraw in Binance API settings
7. **Small position sizes**: Start with small trades (e.g., $1-5)
8. **Use cool-down**: Set `SIGNAL_COOLDOWN_SECONDS` to prevent spam

## Troubleshooting

### "Invalid API credentials"
- Check `BINANCE_API_KEY` and `BINANCE_API_SECRET` in `.env`
- Generate new keys in Binance account
- Ensure testnet keys are used if `USE_TESTNET=true`

### "Webhook secret invalid"
- Check `WEBHOOK_SECRET_KEY` matches in `.env` and TradingView
- Don't use default value, set it to something unique
- If using header auth, format must be: `Authorization: Bearer your-key`

### "Cannot connect to Binance"
- Check internet connection
- Verify `USE_TESTNET` is set correctly
- Check if Binance API is accessible in your region

### "Trades not executing"
- Check account balance (`/health` endpoint)
- Check risk limits in `/status` endpoint
- Verify symbol exists on Binance (e.g., BTCUSDT not BTC)
- Check `logs/signals.csv` for rejection reason

### "Logs not updating"
- Ensure `logs/` directory exists (auto-created)
- Check file permissions on logs directory
- Verify filesystem has space

## Code Structure

### app.py
- FastAPI app with webhook endpoint
- Request validation and security checks
- Trade orchestration
- Status endpoints

### config.py
- Environment variable loading
- Sensible defaults
- Configuration validation

### binance_client.py
- Binance API wrapper
- Order placement (buy/sell)
- Price fetching
- Error handling with proper logging

### risk.py
- Risk constraint checking
- Trade/signal tracking
- Daily limit enforcement
- Duplicate detection

### csv_logger.py
- Thread-safe CSV writing
- Signal logging
- Trade logging
- Error logging

## Example Integration

### TradingView Strategy Alert Example

In your TradingView strategy:

```pinescript
alertsignal = ta.crossover(ta.rsi(close, 14), 30) ? "BUY" : 
              ta.crossunder(ta.rsi(close, 14), 70) ? "SELL" : na

if not na(alertsignal)
    strategy.entry(alertsignal, alertsignal == "BUY" ? strategy.long : strategy.short)
    alert(json.stringify(
        symbol: syminfo.tickerid,
        side: alertsignal,
        strategy: "RSI Strategy",
        timeframe: timeframe.period,
        confidence: 75,
        secret: "your-secret-key"
    ))
```

## Performance Notes

- Webhook processing: <100ms typically
- Binance order placement: 500ms - 2s
- CSV logging: <10ms
- Memory usage: ~50MB idle
- CPU usage: <1% idle, 5-10% during trade

## FAQ

**Q: Can I use this on live trading?**  
A: Yes, but start with testnet and small amounts. Change `USE_TESTNET=false` in `.env`.

**Q: What if my API keys leak?**  
A: Immediately delete the key in Binance and create a new one. The bot won't work with a deleted key.

**Q: Can I run multiple instances?**  
A: Yes, but they'll share the same Binance account. Be careful with cumulative position sizes.

**Q: How do I stop trading?**  
A: Stop the bot process. Or set `MAX_TRADES_PER_DAY=0` to reject all new trades.

**Q: Can I trade other pairs like ETHUSDT?**  
A: Yes, as long as they exist on Binance. Just send them in webhook signals.

**Q: What about leverage/margin trading?**  
A: This bot only does spot trading. Margins/futures not supported (safer this way).

**Q: Can I add stop-loss/take-profit?**  
A: Currently trades are market orders. You can add limit order support in `binance_client.py`.

## Future Enhancements

- Position tracking with stop-loss/take-profit
- Real-time position management
- Portfolio metrics dashboard
- Advanced risk analytics
- Telegram notifications
- Database backend for larger logs
- Multiple strategy support
- Backtesting framework

## Support

- Review logs: `logs/signals.csv` and `logs/trades.csv`
- Check bot status: `curl http://localhost:8000/status`
- API docs: `http://localhost:8000/docs`
- Binance API docs: https://binance-docs.github.io/

## License

MIT License - Feel free to use, modify, and distribute.

## Disclaimer

**THIS IS NOT FINANCIAL ADVICE.** This bot is provided AS-IS without any warranties. Cryptocurrency trading is risky. You can lose your entire investment. Only trade with money you can afford to lose. The creators are not responsible for any losses.

---

**Start with testnet. Start small. Start safe. 🚀**
