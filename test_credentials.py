from binance.client import Client
from config import Config
import json

def test_client(testnet_flag):
    try:
        c = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET, testnet=testnet_flag)
        c.ping()
        acc = c.get_account()
        nonzero = [b for b in acc.get('balances',[]) if float(b.get('free',0))>0]
        return ('OK', nonzero)
    except Exception as e:
        return ('ERROR', str(e))

if __name__ == '__main__':
    print('TESTNET CHECK:')
    print(test_client(True))
    print('\nMAINNET CHECK:')
    print(test_client(False))
