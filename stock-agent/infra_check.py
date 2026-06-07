import sys
import json
import urllib.request
import urllib.error
import asyncio
import os
from dotenv import load_dotenv

print("="*50)
print("🔍 RUNNING PHASE 2 EXTERNAL TOOLS VALIDATION")
print("="*50)

# Step 4: Environment variables sanity check
print("\n[1/4] Checking Environment...")
load_dotenv()
db_url = os.environ.get("DB_URL")
if db_url:
    print(f"✅ Environment variables loaded. DB_URL is securely acquired.", db_url)
else:
    print("❌ Environment checking failed. DB_URL missing from .env.")

# Step 1: Test OpenBB (Data Source)
print("\n[2/4] Testing OpenBB Data Fetching...")
try:
    from openbb import obb
    # Fetch AAPL to satisfy OpenBB basic fetch working
    df = obb.equity.price.historical("AAPL", provider="yfinance").to_df()
    print(f"✅ OpenBB initialized successfully. Fetched {len(df)} historical rows for AAPL.")
except Exception as e:
    print(f"❌ OpenBB failed: {e}")

# Step 3: Test Ollama & Mistral Local Generation
print("\n[3/4] Testing Mistral (Ollama) Generation...")
try:
    # We do a quick completion test to ensure mistral answers
    url = "http://localhost:11434/api/generate"
    data = json.dumps({
        "model": "phi3:mini",
        "prompt": "Say hello world briefly.",
        "stream": False
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        content = response.read()
        res_json = json.loads(content)
        response_text = res_json.get("response", "").strip()
        print(f"✅ phi3:mini responds successfully! Response: '{response_text}'")
except urllib.error.URLError:
    print("❌ Ollama not responding. Is the Ollama app running on localhost:11434?")
except Exception as e:
    print(f"❌ Ollama test failed: {e}")

# Step 2: Test PostgreSQL Connection (Asyncpg)
print("\n[4/4] Testing PostgreSQL Async Hooking...")
async def test_db():
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            print(f"✅ PostgreSQL logic connected smoothly with asyncpg!")
    except Exception as e:
        print(f"❌ PostgreSQL async connection failed: {e}")

# Run Async step hook
if db_url:
    asyncio.run(test_db())

print("\n" + "="*50)
print("Finished Infrastructure Validation for Phase 2!")
print("="*50)
