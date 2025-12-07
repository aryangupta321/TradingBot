import json
from binance.client import Client
from config import Config

try:
    testnet = str(Config.USE_TESTNET).lower() in ("true", "1")
    client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET, testnet=testnet)

    # List recent trades for BTCUSDT (adjust symbol as needed)
    trades = client.get_my_trades(symbol='BTCUSDT', limit=20)
    print(json.dumps(trades, indent=2))
except Exception as e:
    print('ERROR:', str(e))
