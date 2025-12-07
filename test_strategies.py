"""
Quick Test: Send sample scalping and swing trading signals to the bot
to test both strategies on the demo account.
"""
import requests
import json
import time
from config import Config

WEBHOOK_URL = 'https://supervitally-nonsubordinate-tameka.ngrok-free.dev/webhook'
SECRET = Config.WEBHOOK_SECRET_KEY

def send_signal(symbol, side, strategy, timeframe, confidence):
    """Send a signal to the bot and print the response."""
    payload = {
        'symbol': symbol,
        'side': side,
        'strategy': strategy,
        'timeframe': timeframe,
        'confidence': confidence
    }
    
    headers = {
        'Authorization': f'Bearer {SECRET}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n{'='*70}")
    print(f"Sending {strategy} {side} signal for {symbol}")
    print(f"{'='*70}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        resp = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=30)
        print(f"\nStatus: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    print("\n" + "="*70)
    print("TRADING STRATEGY TEST: Scalping + Swing Trading Signals")
    print("="*70)
    
    # Test Scalping Strategy (1-minute, high frequency)
    print("\n\n📊 TESTING SCALPING STRATEGY (1-minute candles, tight stops)")
    print("-" * 70)
    
    send_signal('BTCUSDT', 'BUY', 'Scalping RSI+MACD', '1m', 80)
    time.sleep(2)
    
    send_signal('BTCUSDT', 'SELL', 'Scalping RSI+MACD', '1m', 75)
    time.sleep(2)
    
    send_signal('ETHUSDT', 'BUY', 'Scalping RSI+MACD', '1m', 78)
    time.sleep(2)
    
    # Test Swing Trading Strategy (4-hour, medium frequency)
    print("\n\n📈 TESTING SWING TRADING STRATEGY (4-hour candles, wider stops)")
    print("-" * 70)
    
    send_signal('XRPUSDT', 'BUY', 'Swing Bollinger Bands', '4h', 70)
    time.sleep(2)
    
    send_signal('ADAUSDT', 'BUY', 'Swing Moving Averages', '4h', 68)
    time.sleep(2)
    
    send_signal('SOLUSDT', 'SELL', 'Swing Bollinger Bands', '4h', 65)
    time.sleep(2)
    
    print("\n" + "="*70)
    print("✅ Strategy tests complete! Check logs/signals.csv and logs/trades.csv")
    print("="*70)
