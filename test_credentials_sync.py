#!/usr/bin/env python3
"""
Simple Real Binance Account Validation with Timestamp Sync
"""

import os
from dotenv import load_dotenv
from binance.client import Client
import time

load_dotenv()

print("=" * 70)
print("🔐 REAL BINANCE ACCOUNT VALIDATION")
print("=" * 70)

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
base_url = os.getenv("BINANCE_BASE_URL")

if not api_key or not api_secret:
    print("❌ ERROR: BINANCE_API_KEY or BINANCE_API_SECRET not set in .env")
    exit(1)

print(f"\n📍 API Configuration:")
print(f"   Base URL: {base_url}")
print(f"   API Key (first 16 chars): {api_key[:16]}...")

print("\n⏱️  Syncing server time with Binance...")

try:
    # Try to connect to mainnet
    client = Client(api_key, api_secret, testnet=False)
    
    # Get server time
    server_time = client.get_server_time()
    local_time = int(time.time() * 1000)
    time_diff = abs(server_time['serverTime'] - local_time)
    
    print(f"   Server Time: {server_time['serverTime']}")
    print(f"   Local Time:  {local_time}")
    print(f"   Difference:  {time_diff}ms")
    
    if time_diff > 1000:
        print(f"\n⚠️  WARNING: Time difference > 1 second!")
        print(f"   Your system clock may be out of sync.")
        print(f"   Please sync your system time manually (Windows Settings > Time & Language)")
    
    print(f"\n🔍 Testing API Connection...")
    
    # Get account info
    account = client.get_account()
    
    print(f"✅ SUCCESS! Connected to Real Binance Account")
    print(f"\n📊 Account Information:")
    print(f"   Status: {account.get('accountStatus', 'Unknown')}")
    print(f"   Balances:")
    
    # Show major coin balances
    balances = {b['asset']: float(b['free']) for b in account['balances'] if float(b['free']) > 0}
    
    if balances:
        for coin, amount in sorted(balances.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"     • {coin}: {amount}")
    else:
        print(f"     • No balances found (account may be empty)")
    
    print(f"\n✅ Your real Binance account is connected and ready!")
    
except Exception as e:
    error_str = str(e)
    
    if "-1021" in error_str or "Timestamp" in error_str:
        print(f"\n❌ ERROR: Timestamp out of sync")
        print(f"\n⚠️  FIX: Your computer's clock is out of sync with Binance servers.")
        print(f"\nTo fix this:")
        print(f"1. Right-click System Clock → Adjust date/time")
        print(f"2. Click 'Sync now' button")
        print(f"3. Wait 1-2 seconds")
        print(f"4. Try again: python test_credentials_sync.py")
        print(f"\nAlternative: Check Settings > System > Date & Time > Set time automatically")
    else:
        print(f"\n❌ ERROR: {error_str}")
        if "-2015" in error_str:
            print(f"\n⚠️  Invalid API Key or Secret!")
            print(f"   • Verify API key and secret in .env")
            print(f"   • Make sure API key has TRADE permission enabled")
            print(f"   • If just created, wait 1-2 minutes for Binance to activate it")
        elif "401" in error_str or "403" in error_str:
            print(f"\n⚠️  API Key Rejected!")
            print(f"   • Check if IP whitelist is configured")
            print(f"   • Try removing IP restriction (allow all IPs temporarily)")
            print(f"   • Verify credentials again in .env")

print("\n" + "=" * 70 + "\n")
