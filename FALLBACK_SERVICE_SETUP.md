# 🔄 OpenAI-Compatible Fallback Service Setup

## Overview

The CIFR Agent System now includes an **optional fallback mechanism** that automatically switches to an OpenAI-compatible service when the free tier Google Gemini API hits quota limits (429 errors).

**⚠️ Important for Hackathon:**
- **Primary Service:** Free tier Google Gemini API (for hackathon judges)
- **Fallback Service:** OpenAI-compatible service (demo/backup only - NOT available to hackathon judges)
- The system will **always try the free tier first** - fallback is only used when quota is exhausted

## How It Works

1. **Primary:** System tries Google Gemini API (free tier)
2. **On 429 Error:** If quota exhausted, automatically tries OpenAI-compatible fallback
3. **If Both Fail:** Falls back to heuristic analysis (for hackathon demo)

## Environment Variables

Add these to your `.env` file or set as environment variables:

```env
# Enable fallback service (set to "1" to enable, "0" to disable)
ENABLE_OPENAI_FALLBACK=1

# OpenAI-compatible service base URL
OPENAI_FALLBACK_BASE_URL=https://caas-gocode-prod.caas-prod.prod.onkatana.net/v1

# OpenAI-compatible API key
OPENAI_FALLBACK_API_KEY=sk-k5xL1aEj4Vi0YPPJ3pdxMw

# Model name on the fallback service (must match available models)
OPENAI_FALLBACK_MODEL=gemini-2.0-flash-001
```

## Setup Instructions

### Option 1: Add to .env File

Add these lines to your `.env` file:

```env
ENABLE_OPENAI_FALLBACK=1
OPENAI_FALLBACK_BASE_URL=https://caas-gocode-prod.caas-prod.prod.onkatana.net/v1
OPENAI_FALLBACK_API_KEY=sk-k5xL1aEj4Vi0YPPJ3pdxMw
OPENAI_FALLBACK_MODEL=gemini-2.0-flash-001
```

### Option 2: Set as Environment Variables

When starting the Flask app:

```bash
ENABLE_OPENAI_FALLBACK=1 \
OPENAI_FALLBACK_BASE_URL='https://caas-gocode-prod.caas-prod.prod.onkatana.net/v1' \
OPENAI_FALLBACK_API_KEY='sk-k5xL1aEj4Vi0YPPJ3pdxMw' \
OPENAI_FALLBACK_MODEL='gemini-2.0-flash-001' \
python3 -c "from app import app; app.run(debug=True, host='127.0.0.1', port=9000)"
```

## Available Models on Fallback Service

The fallback service supports these Gemini models:
- `gemini-2.0-flash-001` ✅ (Recommended)
- `gemini-2.0-flash-exp`
- `gemini-2.5-flash`
- `gemini-2.5-flash-image`
- `gemini-2.5-pro`
- And more...

## Behavior

### When Fallback is Enabled (`ENABLE_OPENAI_FALLBACK=1`):

1. **Free Tier Works:** Uses Google Gemini API (primary)
2. **Free Tier Exhausted (429):** Automatically switches to OpenAI-compatible service
3. **Both Fail:** Uses heuristic analysis (for hackathon demo)

### When Fallback is Disabled (`ENABLE_OPENAI_FALLBACK=0` or not set):

1. **Free Tier Works:** Uses Google Gemini API
2. **Free Tier Exhausted (429):** Uses heuristic analysis (for hackathon demo)

## For Hackathon Judges

**Important:** Hackathon judges will **NOT** have access to the fallback service. The system is designed to:

1. **Primary:** Use free tier Google Gemini API (available to all)
2. **Fallback:** Use heuristic analysis when API quota is exhausted
3. **Optional:** Fallback service is only for your personal demo/backup

The system will work perfectly for hackathon judges using only the free tier API and heuristic fallback.

## Testing

To test if the fallback is working:

1. Set `ENABLE_OPENAI_FALLBACK=1`
2. Use a Google Gemini API key that's exhausted (429 error)
3. Make an API call - it should automatically use the fallback service
4. Check logs for: "Using OpenAI-compatible fallback service"

## Troubleshooting

### Fallback Not Working?

1. **Check if enabled:** `ENABLE_OPENAI_FALLBACK=1`
2. **Check base URL:** Must be correct OpenAI-compatible endpoint
3. **Check API key:** Must be valid for the service
4. **Check model name:** Must match available models on the service
5. **Check logs:** Look for error messages in console

### Service Not Available?

If the fallback service is not accessible:
- System will automatically use heuristic analysis
- Hackathon demo will still work
- No action needed - this is expected behavior

## Summary

- ✅ **Primary:** Free tier Google Gemini API (for hackathon)
- ✅ **Fallback:** OpenAI-compatible service (demo/backup only)
- ✅ **Final Fallback:** Heuristic analysis (always works)
- ⚠️ **Hackathon Judges:** Will only use primary + heuristic (no fallback service access)

The system is designed to work perfectly for hackathon judges while providing you with a backup option for demos! 🚀

