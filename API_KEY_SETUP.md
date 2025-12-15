# 🔑 Per-Agent API Key Setup Guide

## Overview
The CIFR Agent System supports **per-agent API keys** to distribute API quota across multiple keys, solving resource exhaustion errors.

## ✅ Current Configuration

The system is already configured to use per-agent keys! Each agent will use its dedicated key if available, or fall back to the default key.

### Agent Key Mapping:
- **Communication Agent** → `GOOGLE_API_KEY_CA`
- **Friction Detection Agent** → `GOOGLE_API_KEY_FA`
- **Intervention Agent** → `GOOGLE_API_KEY_IA`
- **Default Fallback** → `GOOGLE_API_KEY`

## 🚀 How to Set Up Per-Agent Keys

### Option 1: Environment Variables (Recommended)

When starting the Flask app, set all keys:

```bash
GCP_PROJECT_ID='steel-pod-481123-e9' \
GCP_LOCATION='us-central1' \
GOOGLE_API_KEY='AIzaSyA-nv8nAyq8LaCcFk4ZjKk3dV-b_rm_5hA' \
GOOGLE_API_KEY_CA='AIzaSyAdX9HpiIJ-Z7ruwv6etRUd_5cc-WRcEX0' \
GOOGLE_API_KEY_FA='AIzaSyA-nv8nAyq8LaCcFk4ZjKk3dV-b_rm_5hA' \
GOOGLE_API_KEY_IA='AIzaSyDmyetZGSBcQ1QCtee_YtwZAM0iT99e1bM' \
GEMINI_PRO_MODEL_ID='gemini-2.0-flash' \
GEMINI_PRO_VISION_MODEL_ID='gemini-2.5-flash' \
FLASK_SKIP_DOTENV=1 \
python3 -c "from app import app; app.run(debug=True, host='127.0.0.1', port=9000, load_dotenv=False)"
```

### Option 2: .env File

Add to your `.env` file (if readable):

```env
GCP_PROJECT_ID=steel-pod-481123-e9
GCP_LOCATION=us-central1
GOOGLE_API_KEY=AIzaSyA-nv8nAyq8LaCcFk4ZjKk3dV-b_rm_5hA
GOOGLE_API_KEY_CA=AIzaSyAdX9HpiIJ-Z7ruwv6etRUd_5cc-WRcEX0
GOOGLE_API_KEY_FA=AIzaSyA-nv8nAyq8LaCcFk4ZjKk3dV-b_rm_5hA
GOOGLE_API_KEY_IA=AIzaSyDmyetZGSBcQ1QCtee_YtwZAM0iT99e1bM
GEMINI_PRO_MODEL_ID=gemini-2.0-flash
GEMINI_PRO_VISION_MODEL_ID=gemini-2.5-flash
```

## 📊 Benefits of Per-Agent Keys

1. **Distributed Quota**: Each agent uses its own quota limit
2. **Higher Throughput**: 3x the free tier quota (if using 3 different keys)
3. **Fault Isolation**: If one key hits quota, other agents continue working
4. **Scalability**: Easy to add more keys as needed

## 🔍 How to Get Multiple API Keys

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create multiple API keys (one for each agent)
3. Name them clearly (e.g., "CIFR-CA", "CIFR-FA", "CIFR-IA")
4. Copy each key and set the appropriate environment variable

## ✅ Verification

When you start the app, you'll see logging like:

```
🤖 CIFR Agent System - Initializing Agents
============================================================
📋 Project ID: steel-pod-481123-e9
📍 Location: us-central1

🔑 API Key Configuration:
   Default Key: ✅ Set
   Communication Agent (CA): ✅ Using dedicated key
   Friction Detection (FA): ✅ Using dedicated key
   Intervention Agent (IA): ✅ Using dedicated key
============================================================

[Communication Agent] Using dedicated API key (CA): AIzaSyAdX9HpiIJ-Z7...
[Friction Detection Agent] Using dedicated API key (FA): AIzaSyA-nv8nAyq8...
[Intervention Agent] Using dedicated API key (IA): AIzaSyDmyetZGSBcQ1...
```

## 🎯 Best Practices

1. **Use Different Keys**: Use 3 different API keys for maximum quota distribution
2. **Monitor Usage**: Check [Google AI Studio Usage](https://ai.dev/usage?tab=rate-limit) regularly
3. **Rotate Keys**: If a key hits quota, you can rotate to a new key
4. **Enable Billing**: For production, enable billing for higher quotas

## 🚨 Troubleshooting

### If you still see quota errors:

1. **Check Key Status**: Verify keys are active in Google AI Studio
2. **Wait for Reset**: Free tier quotas reset periodically
3. **Use More Keys**: Add additional keys for more quota
4. **Enable Billing**: Production use requires billing for higher limits

### Current Status:

Based on your `.env` file, you have:
- ✅ `GOOGLE_API_KEY_IA` set
- ⚠️ Need to set `GOOGLE_API_KEY_CA` and `GOOGLE_API_KEY_FA` for full per-agent setup

## 📝 Example: Full Per-Agent Setup

```bash
# Get 3 different API keys from Google AI Studio
KEY_1="your-first-api-key"
KEY_2="your-second-api-key"  
KEY_3="your-third-api-key"

# Start app with per-agent keys
GOOGLE_API_KEY_CA=$KEY_1 \
GOOGLE_API_KEY_FA=$KEY_2 \
GOOGLE_API_KEY_IA=$KEY_3 \
python3 -c "from app import app; app.run(debug=True, host='127.0.0.1', port=9000)"
```

This distributes the API calls across 3 different keys, giving you 3x the free tier quota! 🚀

