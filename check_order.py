import json
from binance.client import Client
from config import Config

try:
    testnet = str(Config.USE_TESTNET).lower() in ("true", "1")
    client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET, testnet=testnet)
    order_id = 7534545
    order = client.get_order(symbol='BTCUSDT', orderId=order_id)
    print(json.dumps(order, indent=2))
except Exception as e:
    print('ERROR:', str(e))
