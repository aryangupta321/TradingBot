"""
Try a list of Binance base endpoints for the given API key/secret by calling GET /api/v3/account
This script signs the request using HMAC-SHA256 (standard Binance HMAC keys).
If your key uses Ed25519 or RSA signing, this script will likely fail with -2015.
"""
import time
import hmac
import hashlib
import requests
from config import Config

endpoints = [
    "https://api.binance.com",
    "https://api-gcp.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
    "https://api4.binance.com",
]

API_KEY = Config.BINANCE_API_KEY
API_SECRET = Config.BINANCE_API_SECRET

headers = {"X-MBX-APIKEY": API_KEY}

for base in endpoints:
    try:
        ts = int(time.time() * 1000)
        query = f"timestamp={ts}"
        sig = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
        url = f"{base}/api/v3/account?{query}&signature={sig}"
        print(f"Trying {base} ...")
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        try:
            print(resp.json())
        except Exception:
            print(resp.text[:500])
    except Exception as e:
        print(f"Error contacting {base}: {e}")
    print('\n' + ('-'*60) + '\n')
