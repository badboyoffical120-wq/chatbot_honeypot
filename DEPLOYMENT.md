# Deployment Guide - Render

## Setup Steps

### 1. Create a GitHub Repository
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Render

1. Go to [render.com](https://render.com)
2. Sign up / Log in with GitHub
3. Click "New +" → "Web Service"
4. Choose your repository
5. Fill in the details:
   - **Name**: `scam-detector-api`
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. Set Environment Variables

In Render dashboard, go to your service → Environment:

```
FLASK_SECRET_KEY=your-random-secret-key
HUGGINGFACEHUB_API_TOKEN=hf_xxxxxxxxxxxx
HF_REPO_ID=mistralai/Mistral-7B-Instruct-v0.2
FLASK_ENV=production
PYTHONUNBUFFERED=1
```

### 4. Deploy

- Push changes to main branch → Auto-deploys
- Or manually trigger from Render dashboard

## Testing

```bash
# Get your Render URL from the dashboard
RENDER_URL=https://your-app.onrender.com

# Test API
curl -X POST $RENDER_URL/api/keys/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Production Key"}'

# Use the API key
curl -X POST $RENDER_URL/api/chat \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## Important Notes

- **Free Plan**: Apps spin down after 15 minutes of inactivity
- **Persistent Data**: `api_keys.json` is stored in `/tmp/` and will be lost on redeploy
- For persistent storage, use a database (PostgreSQL recommended)
- Monitor logs in Render dashboard

## Troubleshooting

**Build fails**: Check `requirements.txt` has all dependencies
**502 Bad Gateway**: Check app logs in Render dashboard
**Timeout errors**: Increase "Max Execution Timeout" to 120s
