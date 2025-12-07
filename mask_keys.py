from config import Config

def mask(s):
    if not s:
        return '<EMPTY>'
    s = s.strip()
    if len(s) <= 12:
        return s
    return s[:6] + '...' + s[-6:] + f' (len={len(s)})'

if __name__ == '__main__':
    print('BINANCE_API_KEY:', mask(Config.BINANCE_API_KEY))
    print('BINANCE_API_SECRET:', mask(Config.BINANCE_API_SECRET))
    print('USE_TESTNET:', Config.USE_TESTNET)
