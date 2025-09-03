# 🚀 One-Click Deployment Options

## Option 1: Railway (Recommended)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. Click the button above
2. Connect your GitHub account
3. Select this repository
4. Railway will auto-deploy from the `api/` folder
5. **Cost: FREE** ($5/month credit included)

## Option 2: Render
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click the button above  
2. Connect your GitHub account
3. Point to this repository
4. **Cost: FREE** (free tier available)

## Option 3: Heroku
```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login and create app
heroku login
heroku create your-app-name

# Deploy
git subtree push --prefix api heroku main
```

## Option 4: DigitalOcean App Platform
1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Create new app from GitHub
3. Point to this repository
4. **Cost: $12/month** (most reliable)

---

## 🎯 Recommended Flow:

1. **Start with Railway** (free)
2. **If you need more reliability, upgrade to DigitalOcean**
3. **Your TypeScript client stays the same** - just change the API URL

## 🔧 After Deployment:

Update your `client_extractor.ts` line 12:
```typescript
constructor(apiUrl = 'https://your-railway-app.railway.app', timeout = 30000) {
```

## 💡 Why This Approach is Better:

✅ **No local setup headaches** (M1 Mac compatibility issues)  
✅ **Professional deployment** (auto-scaling, monitoring, logs)  
✅ **Free tier available** (Railway gives $5/month credit)  
✅ **Your Vercel Pro plan stays focused** on your main TypeScript app  
✅ **Separation of concerns** - scraping API separate from main app
