"""
TradingView Alert Configuration Guide and Webhook Payload Templates.

This file contains complete instructions and JSON payload examples for
setting up TradingView alerts to send signals to your trading bot.
"""

TRADINGVIEW_SETUP_GUIDE = """
================================================================================
TRADINGVIEW ALERT SETUP GUIDE FOR YOUR TRADING BOT
================================================================================

Your bot is listening at:
  PUBLIC WEBHOOK URL: https://supervitally-nonsubordinate-tameka.ngrok-free.dev/webhook

Authentication:
  Use the Authorization header with your webhook secret:
  Authorization: Bearer change_this_to_a_random_secret_key_at_least_32_chars

================================================================================
STEP 1: CREATE A TRADINGVIEW STRATEGY OR SCRIPT
================================================================================

Option A: Use a Built-in Strategy
  1. Open TradingView: https://www.tradingview.com
  2. Open a chart (e.g., BTCUSDT, 1-minute timeframe for scalping OR 4h for swing)
  3. Pine Editor (bottom panel) → New → Strategy
  4. Copy one of the example Pine scripts below (see PINE SCRIPT EXAMPLES)
  5. Save and Apply to the chart

Option B: Use Your Own Strategy
  1. If you have an existing strategy, modify it to add alert() calls
  2. Add these lines at buy/sell signals:
     - alertmessage_long = "BUY Signal"
     - alertmessage_short = "SELL Signal"
     - if (buy_condition)
         alert(alertmessage_long, alert.freq_once_per_bar_close)
     - if (sell_condition)
         alert(alertmessage_short, alert.freq_once_per_bar_close)

================================================================================
STEP 2: CREATE AN ALERT IN TRADINGVIEW
================================================================================

After your strategy is applied to a chart:

  1. Click "Alert" button (top-right of chart)
  2. Select your strategy from "Condition" dropdown
  3. Set "Alert name" (e.g., "Scalping BUY", "Swing SELL")
  4. Set "Notification" to "Webhook"
  5. Paste this URL in the webhook URL field:
     https://supervitally-nonsubordinate-tameka.ngrok-free.dev/webhook
  
  6. In "Message" field, paste the appropriate JSON payload (see below)
  7. Click "Create Alert"

================================================================================
STEP 3: WEBHOOK PAYLOAD EXAMPLES
================================================================================

Use these JSON payloads in your TradingView alert "Message" field.

⭐ SCALPING BUY ALERT (1-minute chart):
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "strategy": "Scalping RSI",
  "timeframe": "1m",
  "confidence": 80
}

⭐ SCALPING SELL ALERT (1-minute chart):
{
  "symbol": "BTCUSDT",
  "side": "SELL",
  "strategy": "Scalping RSI",
  "timeframe": "1m",
  "confidence": 75
}

⭐ SWING TRADING BUY ALERT (4-hour chart):
{
  "symbol": "ETHUSDT",
  "side": "BUY",
  "strategy": "Swing Bollinger",
  "timeframe": "4h",
  "confidence": 70
}

⭐ SWING TRADING SELL ALERT (4-hour chart):
{
  "symbol": "ETHUSDT",
  "side": "SELL",
  "strategy": "Swing Bollinger",
  "timeframe": "4h",
  "confidence": 65
}

DYNAMIC PAYLOAD (TradingView variables):
If you want to use TradingView variables in your alert, use this format:
{
  "symbol": "{{ticker}}",
  "side": "{{strategy.order.action}}",
  "strategy": "My Scalping",
  "timeframe": "{{interval}}",
  "confidence": 78
}

Where:
  {{ticker}} = the symbol (e.g., BTCUSDT)
  {{strategy.order.action}} = BUY or SELL
  {{interval}} = the timeframe (e.g., 1m, 4h)

================================================================================
STEP 4: VERIFY ALERT IS FIRING
================================================================================

Test your alert:
  1. In TradingView, go to Alerts (bell icon)
  2. Find your alert in the list
  3. Click "Test" to send a test webhook
  4. Check your bot logs:
     - Open a terminal in your project folder
     - tail -f logs/signals.csv
     - You should see a new row within 2 seconds
  5. Check bot /status endpoint:
     - GET http://localhost:8000/status
     - Should show the signal in recent activity

If you see 401 Unauthorized:
  - Check that the Authorization header is correct
  - Verify WEBHOOK_SECRET_KEY in .env matches what you're using
  - Try sending the webhook with the secret in the JSON body instead:
    {
      "symbol": "BTCUSDT",
      "side": "BUY",
      "strategy": "Scalping",
      "timeframe": "1m",
      "confidence": 80,
      "secret": "change_this_to_a_random_secret_key_at_least_32_chars"
    }

If you see 400 Bad Request:
  - Check JSON syntax (use a JSON validator)
  - Ensure all required fields are present: symbol, side, strategy, timeframe, confidence
  - Confidence should be a number 0-100, not a string

If you see no alert firing at all:
  - Check that the strategy/script is actually generating buy/sell signals
  - Verify alert "Notification" is set to "Webhook" (not Email or Mobile)
  - Check the alert settings in TradingView (Alerts tab)

================================================================================
PINE SCRIPT EXAMPLES (Copy & Paste These)
================================================================================

--- SCALPING STRATEGY: RSI + MACD (1-minute) ---

//@version=5
strategy("Scalping RSI+MACD", overlay=false, max_bars_back=50)

// Parameters
rsi_period = input(14, "RSI Period")
rsi_overbought = input(70, "RSI Overbought")
rsi_oversold = input(30, "RSI Oversold")

// Calculate indicators
rsi = ta.rsi(close, rsi_period)
[macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)

// Buy signal: RSI oversold + MACD crossover
buy_signal = rsi < rsi_oversold and ta.crossover(macdLine, signalLine)
sell_signal = rsi > rsi_overbought and ta.crossunder(macdLine, signalLine)

// Execute strategy
if buy_signal
    strategy.entry("Long", strategy.long)
if sell_signal
    strategy.close("Long")

// Plot for visualization
plot(rsi, "RSI", color.blue)
hline(rsi_overbought, "Overbought", color.red)
hline(rsi_oversold, "Oversold", color.green)
plot(macdLine, "MACD", color.orange)
plot(signalLine, "Signal", color.red)

// Alerts
if buy_signal
    alert("SCALP BUY", alert.freq_once_per_bar_close)
if sell_signal
    alert("SCALP SELL", alert.freq_once_per_bar_close)

--- SWING TRADING STRATEGY: Moving Averages + Bollinger Bands (4h) ---

//@version=5
strategy("Swing Bollinger Bands", overlay=true, max_bars_back=50)

// Parameters
ma_fast = input(20, "Fast MA")
ma_slow = input(50, "Slow MA")
bb_length = input(20, "BB Length")
bb_mult = input(2.0, "BB Mult")

// Calculate indicators
sma_fast = ta.sma(close, ma_fast)
sma_slow = ta.sma(close, ma_slow)
[basis, upper, lower] = ta.bb(close, bb_length, bb_mult)

// Buy signal: Price above slow MA and touches lower BB
buy_signal = close > sma_slow and close < lower and sma_fast > sma_slow
sell_signal = close > upper

// Execute strategy
if buy_signal
    strategy.entry("Long", strategy.long)
if sell_signal
    strategy.close("Long")

// Plot for visualization
plot(sma_fast, "SMA 20", color.blue)
plot(sma_slow, "SMA 50", color.orange)
plot(upper, "BB Upper", color.red)
plot(basis, "BB Basis", color.gray)
plot(lower, "BB Lower", color.green)

// Alerts
if buy_signal
    alert("SWING BUY", alert.freq_once_per_bar_close)
if sell_signal
    alert("SWING SELL", alert.freq_once_per_bar_close)

================================================================================
QUICK START: COPY-PASTE EXAMPLE
================================================================================

1. Open TradingView: https://www.tradingview.com/chart/...
2. Go to Pine Editor → New → Strategy
3. Paste the SCALPING or SWING script above (pick one)
4. Click "Add to chart"
5. Create an Alert:
   - Click "Alert" button
   - Set Condition to your strategy name
   - Set Notification to "Webhook"
   - Webhook URL: https://supervitally-nonsubordinate-tameka.ngrok-free.dev/webhook
   - Message (for scalping BUY on BTCUSDT):
     {
       "symbol": "BTCUSDT",
       "side": "BUY",
       "strategy": "Scalping RSI",
       "timeframe": "1m",
       "confidence": 80
     }
   - Click "Create"

6. Test the alert:
   - In TradingView, click "Alerts" (bell icon)
   - Find your alert and click "Test"
   - In your bot terminal, run: tail -f logs/signals.csv
   - You should see a new row appear in 1-2 seconds

7. DONE! Your bot will now execute trades based on TradingView signals.

================================================================================
STRATEGY TIPS TO MAXIMIZE WIN RATE
================================================================================

SCALPING TIPS:
  ✓ Use 1-minute candles and fast indicators (RSI, MACD, ATR)
  ✓ Trade only during high-volatility hours (first 1h after US open, Asian open)
  ✓ Require confidence 75%+ (strict entry rules)
  ✓ Use tight stops (0.3%) to limit risk
  ✓ Take quick profits (0.5%) to avoid reversals
  ✓ Focus on BTC and ETH (most liquid)
  ✓ Expect 70%+ win rate to be profitable (tight stops = many winners)

SWING TRADING TIPS:
  ✓ Use 4-hour or daily candles (avoid noise)
  ✓ Trade confirmed support/resistance levels
  ✓ Wait for moving average alignment (trend confirmation)
  ✓ Use Bollinger Bands or RSI for entry timing
  ✓ Set wider stops (2-3%) to avoid stop hunts
  ✓ Allow larger profits (3-5%) to capture trends
  ✓ Focus on pairs with clear trends
  ✓ Expect 50-60% win rate (wider stops = fewer winners but bigger gains)

GENERAL RULES:
  ✓ Risk only 1-2% of account per trade
  ✓ Have a predefined exit plan (TP + SL)
  ✓ Log all trades and review weekly
  ✓ Adjust strategy based on market conditions
  ✓ Never add to losing positions
  ✓ Treat small losses as tuition (learning cost)
  ✓ Be consistent with your rules

================================================================================
"""

if __name__ == '__main__':
    print(TRADINGVIEW_SETUP_GUIDE)
