#!/usr/bin/env python3
"""Test script to check which API keys have exhausted their quota"""

import os
import sys
import google.genai as genai
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except:
    pass

# Import config
sys.path.insert(0, os.path.dirname(__file__))
from cifr_agent_system.config import Config

def test_api_key(key_name, api_key, model="gemini-2.0-flash"):
    """Test a single API key"""
    if not api_key:
        return {"status": "not_set", "key_name": key_name}
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=[{"parts": [{"text": "Hello, this is a test."}]}]
        )
        
        if response.candidates:
            return {
                "status": "working",
                "key_name": key_name,
                "key_preview": api_key[:20] + "...",
                "response": response.candidates[0].content.parts[0].text[:50] + "..."
            }
        else:
            return {"status": "no_response", "key_name": key_name}
            
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
            return {
                "status": "quota_exhausted",
                "key_name": key_name,
                "key_preview": api_key[:20] + "...",
                "error": "Quota exceeded - 429 RESOURCE_EXHAUSTED"
            }
        else:
            return {
                "status": "error",
                "key_name": key_name,
                "key_preview": api_key[:20] + "...",
                "error": str(e)[:100]
            }

def main():
    print("="*70)
    print("🔍 CIFR Agent System - API Key Quota Diagnostic")
    print("="*70)
    print()
    
    # Test all keys
    keys_to_test = [
        ("Default Key (GOOGLE_API_KEY)", Config.GOOGLE_API_KEY),
        ("Communication Agent (GOOGLE_API_KEY_CA)", Config.GOOGLE_API_KEY_CA),
        ("Friction Detection Agent (GOOGLE_API_KEY_FA)", Config.GOOGLE_API_KEY_FA),
        ("Intervention Agent (GOOGLE_API_KEY_IA)", Config.GOOGLE_API_KEY_IA),
    ]
    
    results = []
    for key_name, api_key in keys_to_test:
        print(f"Testing {key_name}...", end=" ", flush=True)
        result = test_api_key(key_name, api_key)
        results.append(result)
        
        if result["status"] == "working":
            print("✅ WORKING")
        elif result["status"] == "quota_exhausted":
            print("❌ QUOTA EXHAUSTED")
        elif result["status"] == "not_set":
            print("⚠️  NOT SET")
        elif result["status"] == "error":
            print(f"❌ ERROR: {result.get('error', 'Unknown error')[:50]}")
        else:
            print(f"⚠️  {result['status'].upper()}")
    
    print()
    print("="*70)
    print("📊 Summary Report")
    print("="*70)
    print()
    
    working_keys = [r for r in results if r["status"] == "working"]
    exhausted_keys = [r for r in results if r["status"] == "quota_exhausted"]
    not_set_keys = [r for r in results if r["status"] == "not_set"]
    error_keys = [r for r in results if r["status"] == "error"]
    
    if working_keys:
        print("✅ WORKING KEYS:")
        for r in working_keys:
            print(f"   • {r['key_name']}: {r.get('key_preview', 'N/A')}")
        print()
    
    if exhausted_keys:
        print("❌ QUOTA EXHAUSTED KEYS:")
        for r in exhausted_keys:
            print(f"   • {r['key_name']}: {r.get('key_preview', 'N/A')}")
            print(f"     → {r.get('error', 'Quota limit reached')}")
        print()
    
    if not_set_keys:
        print("⚠️  NOT CONFIGURED:")
        for r in not_set_keys:
            print(f"   • {r['key_name']}")
        print()
    
    if error_keys:
        print("❌ ERROR KEYS:")
        for r in error_keys:
            print(f"   • {r['key_name']}: {r.get('error', 'Unknown error')}")
        print()
    
    print("="*70)
    print("💡 Recommendations:")
    print("="*70)
    
    if exhausted_keys:
        print("1. Replace exhausted keys with new API keys from Google AI Studio")
        print("2. Wait for quota reset (usually resets every minute/hour)")
        print("3. Enable billing for higher quotas")
    
    if len(working_keys) < 3:
        print(f"4. Configure {3 - len(working_keys)} more working keys for full per-agent setup")
    
    print()
    print("🔗 Get new API keys: https://aistudio.google.com/app/apikey")
    print("📊 Check usage: https://ai.dev/usage?tab=rate-limit")
    print()

if __name__ == "__main__":
    main()

