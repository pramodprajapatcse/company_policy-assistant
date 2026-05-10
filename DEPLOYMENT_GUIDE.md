# Deployment Guide - Render

## ✅ Current Status: Successfully Deployed on Render

Your AI Policy Assistant is **live and running** at:
### 🌐 https://company-project-f3ae.onrender.com

---

## 📋 What's Deployed

- **Backend API** - FastAPI endpoints for policy queries
- **Frontend UI** - Chat interface served at root URL
- **Documents** - 100+ policy documents indexed
- **Vector Search** - Hybrid search with ChromaDB
- **LLM Integration** - NVIDIA API for responses
- **Streaming** - Real-time response streaming

---

## 🔐 Environment Configuration

The following environment variables are configured on Render:

```
NVIDIA_API_KEY          # Your NVIDIA API key
LLM_PROVIDER           # Set to: nvidia
NVIDIA_API_BASE_URL    # https://integrate.api.nvidia.com/v1
LOG_LEVEL              # INFO (default)
```

---

## 📊 Monitoring

### View Logs
1. Go to https://render.com/dashboard
2. Click **company-policy-assistant**
3. Click **Logs** tab
4. See real-time application logs

### Health Check
```bash
curl https://company-project-f3ae.onrender.com/api/v1/health
```

---

## 🔄 Auto-Deployment

Changes are automatically deployed when you push to GitHub:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Render will automatically:
1. Pull changes from GitHub
2. Build Docker image
3. Deploy new version
4. Restart the service

---

## 📝 Making Changes

### Update Policy Documents
1. Add `.txt` files to `data/policies/`
2. Commit and push to GitHub
3. Render auto-deploys with updated documents

### Update Frontend
1. Edit `static/index.html`, `static/styles.css`, or `static/script.js`
2. Commit and push to GitHub
3. Changes live in ~5 minutes

### Update Backend
1. Edit files in `app/` directory
2. Commit and push to GitHub
3. Render rebuilds and deploys

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| 500 API error | Check NVIDIA_API_KEY in Render settings |
| Deployment failed | Check build logs in Render dashboard |
| Streaming not working | Verify endpoint `/api/v1/query/stream` exists |
| Logo not showing | Check `static/MAHINDRALOGO.jpeg` exists |

---

## 📚 Reference Guides

- **Full Documentation**: See `README.md`
- **Technical Details**: See `RENDER_DEPLOYMENT_GUIDE.md`
- **API Reference**: See `README.md` → API Endpoints section

---

**Last Updated:** May 11, 2026  
**Deployment Platform:** Render  
**Status:** ✅ Live