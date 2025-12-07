# Architecture & Design Documentation

## Overview

This trading bot is designed with **safety, simplicity, and reliability** as core principles.

```
┌─────────────────────┐
│   TradingView       │
│   (Sends Signals)   │
└──────────┬──────────┘
           │
           │ HTTPS POST /webhook
           │ (with secret key)
           │
           ▼
┌─────────────────────────────────────────┐
│        FastAPI Server (app.py)          │
│  - Webhook receiver                     │
│  - Request validation                   │
│  - Secret key verification              │
└──────────┬──────────────────────────────┘
           │
           ├─────────────────┬─────────────────┬──────────────┐
           ▼                 ▼                 ▼              ▼
    ┌──────────────┐ ┌──────────────┐ ┌────────────────┐ ┌─────────────┐
    │  Risk Engine │ │CSV Logger    │ │ Binance Client │ │  Config     │
    │  (risk.py)   │ │(csv_logger)  │ │(binance_client)│ │(config.py)  │
    │              │ │              │ │                │ │             │
    │ - Validate   │ │ - Log signals│ │ - Get prices   │ │ - Load env  │
    │ - Limits     │ │ - Log trades │ │ - Execute buy  │ │ - Defaults  │
    │ - Cooldown   │ │ - CSV format │ │ - Execute sell │ │ - Validate  │
    │ - Tracking   │ │ - Thread-safe│ │ - Order status │ │             │
    └──────────────┘ └──────────────┘ └────────────────┘ └─────────────┘
           │
           └─────────────────┬──────────────────────────────┐
                             │                              │
                             ▼                              ▼
                    ┌──────────────────┐         ┌──────────────────┐
                    │  CSV Logs        │         │  Binance API     │
                    │  - signals.csv   │         │  - Testnet       │
                    │  - trades.csv    │         │  - Live Trading  │
                    └──────────────────┘         └──────────────────┘
```

## Module Breakdown

### 1. **app.py** - FastAPI Webhook Server

**Responsibility**: Receive signals and orchestrate trading

**Key Components**:
- `POST /webhook` - Main entry point for TradingView alerts
- `GET /health` - Health check endpoint
- `GET /status` - Bot status and risk metrics
- `execute_trade()` - Orchestrates risk check → trade execution → logging

**Flow**:
```
1. Receive webhook request
2. Validate secret key (security gate)
3. Parse JSON payload (data validation)
4. Get account balance
5. Run risk engine checks
6. Log signal decision
7. If approved: execute trade
8. Return response to TradingView
```

**Error Handling**:
- 401 Unauthorized - Invalid/missing secret
- 400 Bad Request - Invalid JSON format
- 500 Internal Server Error - Server exceptions

### 2. **config.py** - Configuration Management

**Responsibility**: Load and validate all settings from environment

**Key Features**:
- Single source of truth for all configuration
- Environment variable loading with defaults
- Configuration validation on startup
- Raises clear errors if critical values missing

**Settings Categories**:
- API Credentials (Binance keys)
- Webhook Security (secret key)
- Risk Parameters (limits, thresholds)
- Server Settings (host, port)
- Logging (CSV paths)

**Why This Approach**:
- Easy to change without code edits
- Railway/cloud-friendly
- Secure (secrets not in code)
- Validated at startup (fail fast)

### 3. **risk.py** - Risk Management Engine

**Responsibility**: Prevent dangerous trades through constraint checking

**Key Constraints** (checked in order):
```
1. Confidence ≥ MIN_CONFIDENCE
2. Balance ≥ MIN_BALANCE_USDT
3. Trade size ≤ MAX_RISK_PER_TRADE
4. Open trades < MAX_OPEN_TRADES
5. Trades today < MAX_TRADES_PER_DAY
6. Signal not in cooldown period
```

**Thread Safety**:
- Uses `threading.Lock()` for concurrent access
- Safe for multiple webhook requests simultaneously

**Tracking**:
- `_signal_cache` - Prevent duplicate signals (cooldown)
- `_trades_today` - Count daily executions
- `_open_trades` - Track open positions
- Auto-resets daily counters at midnight UTC

**Why These Constraints**:
- **Confidence**: Reject low-confidence signals
- **Balance**: Prevent trading with insufficient funds
- **Risk per trade**: Cap maximum loss per trade
- **Open limit**: Prevent over-leverage
- **Daily limit**: Prevent over-trading
- **Cooldown**: Prevent spam/loop trading

### 4. **binance_client.py** - Binance API Wrapper

**Responsibility**: Abstract Binance API with error handling

**Key Methods**:
```python
get_account_balance(asset)        # Get USDT balance
get_current_price(symbol)         # Get market price
calculate_buy_quantity(symbol, amount)  # Right qty for amount
place_buy_order(symbol, qty, price)     # Buy order
place_sell_order(symbol, qty, price)    # Sell order
get_order_status(symbol, order_id)      # Check order
cancel_order(symbol, order_id)          # Cancel
```

**Error Handling**:
- Catches Binance-specific exceptions
- Catches network errors
- Returns None on error (fail gracefully)
- Logs all errors with context

**Testnet/Live Support**:
- Reads `USE_TESTNET` config
- Auto-selects correct endpoint
- Same code works for both

**Why Abstraction**:
- Hide API complexity
- Centralized error handling
- Easy to test/mock
- Easy to modify API calls

### 5. **csv_logger.py** - CSV Logging

**Responsibility**: Thread-safe CSV logging for Excel analysis

**Files Generated**:
- `logs/signals.csv` - All signal decisions
- `logs/trades.csv` - All executed trades

**Thread Safety**:
- Uses `threading.Lock()` for writes
- Safe for concurrent logging

**Headers**:

**signals.csv**:
```
DateTime,TradingPair,Action,Strategy,TimeFrame,Confidence,Decision,Reason
```

**trades.csv**:
```
DateTime,TradingPair,Action,TradeAmount,Price,OrderID,Status
```

**Why CSV**:
- Excel-compatible (no database needed)
- Human-readable
- Easy to analyze/audit
- Works offline
- No external dependencies

## Data Flow Examples

### Example 1: Signal Accepted and Executed

```
1. TradingView sends: BUY BTCUSDT, confidence 75
2. app.py receives webhook
3. Secret key validated ✓
4. JSON parsed ✓
5. Get balance: $100 USDT ✓
6. Risk engine checks:
   - Confidence 75 ≥ 50 ✓
   - Balance $100 ≥ $10 ✓
   - Risk $10 ≤ $10 ✓
   - Open trades 0 < 3 ✓
   - Trades today 0 < 10 ✓
   - No recent BUY BTCUSDT ✓
7. Log signal: ACCEPTED
8. Get current price: $43,000
9. Calculate qty: $10 / $43,000 = 0.000233 BTC
10. Place buy order → Binance
11. Receive order ID: 123456
12. Log trade: FILLED
13. Return 200 OK to TradingView
```

### Example 2: Signal Rejected - Daily Limit

```
1. TradingView sends: BUY ETHUSDT, confidence 60
2. app.py receives webhook
3. Secret key validated ✓
4. JSON parsed ✓
5. Get balance: $100 USDT ✓
6. Risk engine checks:
   - Confidence 60 ≥ 50 ✓
   - Balance $100 ≥ $10 ✓
   - Risk $10 ≤ $10 ✓
   - Open trades 2 < 3 ✓
   - Trades today 10 < 10 ✗ REJECTED
7. Log signal: REJECTED, reason = "Daily limit reached"
8. Return 200 OK with decision: REJECTED
9. NO trade executed (safety!)
```

### Example 3: Signal Rejected - Low Confidence

```
1. TradingView sends: SELL BNBUSDT, confidence 25
2. app.py receives webhook
3. Secret key validated ✓
4. JSON parsed ✓
5. Get balance: $100 USDT ✓
6. Risk engine checks:
   - Confidence 25 ≥ 50 ✗ REJECTED
7. Log signal: REJECTED, reason = "Confidence below minimum"
8. Return 200 OK with decision: REJECTED
9. NO trade executed (safety!)
```

## Security Architecture

### Webhook Security

**Multi-layered approach**:

1. **Secret Key Validation**
   - Accept secret from header: `Authorization: Bearer key`
   - Or from JSON body: `{"secret": "key"}`
   - Compare against `WEBHOOK_SECRET_KEY` from config
   - Reject if mismatch (401 Unauthorized)

2. **Payload Validation**
   - Pydantic validates JSON structure
   - Type checking (symbol is string, confidence is 0-100)
   - Auto-uppercase symbol and side
   - Reject if invalid (400 Bad Request)

3. **API Key Security**
   - API keys NOT hardcoded (stored in .env)
   - .env in .gitignore (not committed to git)
   - Support for IP whitelist in Binance
   - Withdraw permission disabled

### Risk Layer

Acts as second line of defense:
- Even if auth bypassed, risk engine prevents large losses
- Daily/position limits prevent catastrophic trading
- Minimum balance prevents margin calls
- Confidence threshold prevents low-quality signals

### Code Safety

- No eval() or exec() (prevents code injection)
- Input validation on all external data
- Try-catch blocks around all API calls
- Graceful degradation on errors
- Comprehensive logging for audit trail

## Scalability Considerations

### Current Design (Single Instance)

Works well for:
- One person trading one strategy
- < 100 trades/day
- One Binance account
- Testnet + small live accounts

**Limits**:
- One process instance only
- No distributed state tracking
- CSV logs not persistent in cloud (ephemeral)

### For Scaling Up

Would need:
1. **Database** (PostgreSQL, MongoDB)
   - Replace CSV with persistent storage
   - Track positions across restarts
   - Query historical data

2. **Message Queue** (Redis, RabbitMQ)
   - Decouple webhook receiving from execution
   - Retry failed trades
   - Multiple workers processing signals

3. **Multiple Instances**
   - Load balancer (nginx)
   - Shared state in database
   - Prevent duplicate trades

4. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert on anomalies

For now, keep it simple! Single instance works great for most users.

## Testing Strategy

### Unit Tests (Not Included)

Could add:
```python
# test_risk_engine.py
def test_confidence_threshold():
    allowed, reason = risk_engine.check_all_constraints(...)
    assert not allowed
    assert "confidence" in reason.lower()

# test_binance_client.py
def test_get_price_error_handling():
    # Mock API error
    assert client.get_current_price("FAKE") is None
```

### Integration Testing

Manual testing recommended:
```bash
# 1. Start bot on testnet
python app.py

# 2. Send test signals
curl -X POST http://localhost:8000/webhook ...

# 3. Verify logs
cat logs/signals.csv

# 4. Check Binance testnet orders
# Go to https://testnet.binance.vision/trade/BTCUSDT
```

### Deployment Testing

Before going live:
1. ✅ Run on testnet for 1 week
2. ✅ Review all trades in logs
3. ✅ Verify risk limits are working
4. ✅ Test emergency stop (restart app)
5. ✅ Verify logs persist correctly

## Performance Metrics

**Expected Performance** (on standard server):

- Webhook latency: 50-200ms
- Binance API call: 500ms - 2s
- CSV write: < 10ms
- Memory usage: ~50MB idle
- CPU: < 1% idle, 10% during trade execution

**Bottlenecks**:
1. Binance API (slowest, external dependency)
2. Network latency (affects Binance)
3. CSV disk I/O (negligible)

**Optimizations** (if needed):
- Use async database instead of CSV
- Cache price data locally
- Batch trades if volume grows
- Use faster serialization (MessagePack vs JSON)

## Why This Architecture?

**Design Principles**:

1. **Safety First**
   - Multiple risk checks prevent losses
   - Fail-safe defaults (reject on error)
   - Comprehensive logging for audit

2. **Simplicity**
   - Single process, no queue/workers
   - CSV instead of database
   - Minimal dependencies
   - Easy to understand and modify

3. **Clarity**
   - Each module has single responsibility
   - Clear separation of concerns
   - Well-commented code
   - Error messages explain "why"

4. **Reliability**
   - Error handling throughout
   - Graceful degradation
   - Thread-safe operations
   - Clear startup/shutdown

5. **Beginner-Friendly**
   - No complex patterns
   - Standard Python libraries
   - Easy to debug
   - Lots of comments and examples

## Future Enhancement Ideas

1. **Position Management**
   - Stop-loss orders
   - Take-profit levels
   - Trailing stops

2. **Notifications**
   - Telegram alerts
   - Email summaries
   - SMS on errors

3. **Analytics**
   - Win rate tracking
   - Profit/loss calculation
   - Sharpe ratio
   - Strategy performance

4. **Advanced Features**
   - Portfolio rebalancing
   - Correlation analysis
   - Machine learning signals
   - Backtesting engine

Start simple, add features as needed! 🚀

---

This architecture prioritizes **safety and simplicity** over complexity. It's designed for beginners to understand and professionals to rely on.
