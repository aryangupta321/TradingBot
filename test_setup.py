"""
Quick test script to validate trading bot setup.
Run this to check if everything is configured correctly before deployment.

Usage:
  python test_setup.py
"""

import sys
import os


def test_imports():
    """Test that all required modules can be imported."""
    print("\n" + "=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    
    try:
        import fastapi
        print("✓ FastAPI installed")
    except ImportError:
        print("✗ FastAPI NOT installed - run: pip install fastapi")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn installed")
    except ImportError:
        print("✗ Uvicorn NOT installed - run: pip install uvicorn")
        return False
    
    try:
        import binance
        print("✓ python-binance installed")
    except ImportError:
        print("✗ python-binance NOT installed - run: pip install python-binance")
        return False
    
    try:
        import pydantic
        print("✓ Pydantic installed")
    except ImportError:
        print("✗ Pydantic NOT installed - run: pip install pydantic")
        return False
    
    try:
        import dotenv
        print("✓ python-dotenv installed")
    except ImportError:
        print("✗ python-dotenv NOT installed - run: pip install python-dotenv")
        return False
    
    return True


def test_files():
    """Check that all required files exist."""
    print("\n" + "=" * 60)
    print("TESTING PROJECT FILES")
    print("=" * 60)
    
    required_files = [
        'app.py',
        'config.py',
        'csv_logger.py',
        'risk.py',
        'binance_client.py',
        'requirements.txt',
        'README.md',
        '.env.example',
        '.gitignore',
        'logs',
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} NOT FOUND")
            all_exist = False
    
    return all_exist


def test_config():
    """Test configuration loading."""
    print("\n" + "=" * 60)
    print("TESTING CONFIGURATION")
    print("=" * 60)
    
    try:
        from config import Config, validate_config
        
        print(f"✓ Config module imported successfully")
        
        # Check if .env exists
        if os.path.exists('.env'):
            print("✓ .env file exists")
        else:
            print("⚠ .env file NOT found - copy from .env.example")
            print("  Run: cp .env.example .env")
            return False
        
        # Try to load config
        try:
            validate_config()
            print("✓ Configuration validated")
            return True
        except ValueError as e:
            print(f"✗ Configuration error: {e}")
            print("  Update .env with your actual API keys")
            return False
    
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return False


def test_logging():
    """Test CSV logging setup."""
    print("\n" + "=" * 60)
    print("TESTING CSV LOGGING")
    print("=" * 60)
    
    try:
        from csv_logger import logger
        
        print("✓ CSV logger imported")
        
        # Check logs directory
        if os.path.exists('logs'):
            print("✓ logs/ directory exists")
        else:
            print("✗ logs/ directory not found")
            return False
        
        # Test logging
        logger.log_info("Test message")
        print("✓ Logging works")
        
        return True
    
    except Exception as e:
        print(f"✗ Error testing logger: {e}")
        return False


def test_risk_engine():
    """Test risk engine initialization."""
    print("\n" + "=" * 60)
    print("TESTING RISK ENGINE")
    print("=" * 60)
    
    try:
        from risk import risk_engine
        from config import Config
        
        print("✓ Risk engine imported")
        
        # Test constraint checking
        allowed, reason = risk_engine.check_all_constraints(
            symbol="BTCUSDT",
            action="BUY",
            confidence=75,
            account_balance=100
        )
        
        if allowed or reason:
            print(f"✓ Risk engine check works")
            print(f"  Result: {reason}")
            return True
        else:
            print("✗ Risk engine returned invalid result")
            return False
    
    except Exception as e:
        print(f"✗ Error testing risk engine: {e}")
        return False


def test_fastapi_imports():
    """Test FastAPI imports."""
    print("\n" + "=" * 60)
    print("TESTING FASTAPI APP")
    print("=" * 60)
    
    try:
        # Note: Don't actually run the app, just check imports
        from fastapi import FastAPI, Request, HTTPException
        from pydantic import BaseModel, Field, validator
        
        print("✓ FastAPI imports successful")
        return True
    
    except Exception as e:
        print(f"✗ Error importing FastAPI: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TRADING BOT SETUP VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Project Files", test_files),
        ("Configuration", test_config),
        ("CSV Logging", test_logging),
        ("Risk Engine", test_risk_engine),
        ("FastAPI", test_fastapi_imports),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Unexpected error in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 60)
        print("✓ ALL CHECKS PASSED - BOT IS READY TO RUN!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Verify .env has your real Binance API keys")
        print("2. Run: python app.py")
        print("3. Test webhook: curl http://localhost:8000/docs")
        print("\nFor Railway deployment, see RAILWAY_DEPLOYMENT.md")
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ SETUP INCOMPLETE - FIX ERRORS ABOVE")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
