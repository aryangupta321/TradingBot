import requests
import time, hmac, hashlib
from config import Config
API_KEY=Config.BINANCE_API_KEY
API_SECRET=Config.BINANCE_API_SECRET
headers={'X-MBX-APIKEY':API_KEY}
try_urls=[
    'https://demo.binance.com',
    'https://demo.binance.com/api',
    'https://demo.binance.com/api/v3',
    'https://demo.binance.com/api/v3/account',
    'https://demo-api.binance.com',
    'https://api-demo.binance.com',
    'https://api.demo.binance.com'
]
for base in try_urls:
    try:
        ts=int(time.time()*1000)
        q=f'timestamp={ts}'
        sig=hmac.new(API_SECRET.encode(), q.encode(), hashlib.sha256).hexdigest()
        if base.endswith('/api/v3/account'):
            url=f"{base}?{q}&signature={sig}"
        else:
            url=f"{base}/api/v3/account?{q}&signature={sig}"
        print('Trying',url)
        r=requests.get(url, headers=headers, timeout=8)
        print(r.status_code)
        try:
            print(r.json())
        except:
            print(r.text[:300])
    except Exception as e:
        print('ERR',e)
    print('-'*40)
