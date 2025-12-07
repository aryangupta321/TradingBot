#!/usr/bin/env python3
import requests
import json
from config import Config

public_url = 'https://supervitally-nonsubordinate-tameka.ngrok-free.dev'
webhook_url = f'{public_url}/webhook'
secret = Config.WEBHOOK_SECRET_KEY

# Test payload
payload = {
    'symbol': 'ETHUSDT',
    'side': 'BUY',
    'strategy': 'DemoTest',
    'timeframe': '1h',
    'confidence': 75
}

headers = {
    'Authorization': f'Bearer {secret}',
    'Content-Type': 'application/json'
}

print(f'Sending webhook to: {webhook_url}')
print(f'Payload: {json.dumps(payload, indent=2)}\n')

try:
    resp = requests.post(webhook_url, json=payload, headers=headers, timeout=30)
    print(f'Status Code: {resp.status_code}')
    print(f'Response: {json.dumps(resp.json(), indent=2)}')
except Exception as e:
    print(f'Error: {e}')
