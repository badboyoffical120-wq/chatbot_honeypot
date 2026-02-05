# Environment Variables Setup for Render

## What are Environment Variables?

Environment variables are configuration values that are stored separately from your code. They're used for:
- API keys and secrets
- Database credentials
- Configuration settings
- Different settings per environment (dev/production)

## Environment Variables Needed for Your App

Your Flask app needs these environment variables:

### Required Variables

1. **HUGGINGFACEHUB_API_TOKEN** (Required)
   - Your Hugging Face API token
   - Get it from: https://huggingface.co/settings/tokens

2. **HF_REPO_ID** (Optional)
   - Model to use
   - Default: `mistralai/Mistral-7B-Instruct-v0.2`
   - Example: `mistralai/Mistral-7B-Instruct-v0.2`

3. **FLASK_SECRET_KEY** (Recommended)
   - Secret key for Flask sessions
   - Generate a random string

4. **FLASK_ENV** (Recommended)
   - Set to: `production`

5. **PYTHONUNBUFFERED** (Recommended)
   - Set to: `1`
   - Ensures output buffering is disabled

## How to Set on Render

### Step 1: Go to Render Dashboard
1. Visit: https://render.com/dashboard
2. Select your web service

### Step 2: Click Environment
- In the service page, click the **"Environment"** tab

### Step 3: Add Variables
Click **"Add Environment Variable"** and enter each one:

```
HUGGINGFACEHUB_API_TOKEN = hf_xxxxxxxxxxxx_your_token_here
HF_REPO_ID = mistralai/Mistral-7B-Instruct-v0.2
FLASK_SECRET_KEY = your-random-secret-key-here
FLASK_ENV = production
PYTHONUNBUFFERED = 1
```

### Step 4: Save and Deploy
- Click "Save Changes"
- Render will automatically redeploy with new variables

## Getting Your Tokens

### Get Hugging Face Token:
1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: "Render Deployment"
4. Type: Read (to read models)
5. Create token
6. Copy the token

### Generate Flask Secret Key:
```python
import secrets
print(secrets.token_urlsafe(32))
```

## Reading Variables in Your Code

Your `app.py` already reads these correctly:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # For local development

# Read from environment
api_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
repo_id = os.environ.get("HF_REPO_ID", "mistralai/Mistral-7B-Instruct-v0.2")
secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
flask_env = os.environ.get("FLASK_ENV", "development")
```

## Local Development (.env file)

For local development, create `.env` in your project root:

```
HUGGINGFACEHUB_API_TOKEN=hf_xxxxxxxxxxxx
HF_REPO_ID=mistralai/Mistral-7B-Instruct-v0.2
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=development
```

⚠️ **IMPORTANT**: Never commit `.env` to GitHub!
Your `.gitignore` already excludes it ✓

## Render Environment Variables vs .env

| Feature | Local (.env) | Render (Dashboard) |
|---------|-------------|------------------|
| Used for | Development | Production |
| Stored where | Project folder | Render servers |
| Visible in code | No (git ignored) | No (secure) |
| Takes priority | Second (after system) | First |
| Edit from | Text editor | Render dashboard |

## Troubleshooting

### "Missing HUGGINGFACEHUB_API_TOKEN"
- Go to Render dashboard
- Environment tab
- Add the token variable
- Redeploy

### "Model access denied"
- Check token has read permissions
- Verify HF_REPO_ID exists and is public
- Some models require access request on HuggingFace

### Variables not updating
- Render caches settings
- Click "Deploy" or update code to trigger redeploy

## Viewing Logs on Render

To debug environment issues:
1. Go to your Render service
2. Click "Logs"
3. Look for error messages

## API Key Management in Your App

Your app also stores API keys in `api_keys.json`. These are:
- **Local**: Stored in `api_keys.json` file
- **Render**: Lost on redeploy (ephemeral filesystem)

For production, consider:
- Using a database (PostgreSQL on Render)
- Or accept reset on redeploy

## Summary Checklist

- [ ] Get Hugging Face token
- [ ] Generate Flask secret key
- [ ] Go to Render dashboard
- [ ] Add environment variables
- [ ] Redeploy app
- [ ] Test API endpoints
