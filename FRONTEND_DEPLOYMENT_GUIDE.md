# Frontend Deployment - Currently Served from Render Backend

## 📌 Note

The frontend is **no longer deployed separately**. It is now served directly from the Render backend at:
### 🌐 https://company-project-f3ae.onrender.com

---

## Why Consolidated Deployment?

✅ **Advantages:**
- Single deployment to manage
- No CORS issues
- Faster response times
- Easier environment management
- Reduced deployment complexity
- Unified logging and monitoring

---

## Frontend Files

The frontend is located in the `static/` directory:

```
static/
├── index.html              # Chat UI
├── styles.css              # Mahindra branding & styling
├── script.js               # Chat logic & API integration
└── MAHINDRALOGO.jpeg       # Company logo
```

---

## Making Frontend Changes

### Edit HTML/CSS/JavaScript
1. Edit files in `static/` folder
2. Commit and push to GitHub
3. Render auto-deploys (~5 minutes)

### Example Changes
```bash
# Edit styles
vim static/styles.css

# Edit chat interface
vim static/index.html

# Commit and deploy
git add static/
git commit -m "Update frontend styles"
git push origin main
```

---

## Features

- ✅ Real-time chat interface
- ✅ Streaming responses (ChatGPT-style)
- ✅ Policy categories sidebar
- ✅ Quick question tags
- ✅ Mahindra branding
- ✅ Responsive design (mobile & desktop)
- ✅ Loading indicators
- ✅ Error handling

---

## Testing Locally

```bash
# Start the FastAPI backend
python -m uvicorn app.main:app --reload

# Visit http://localhost:8000
```

The frontend will automatically call the local API at `/api/v1/`.

---

## API Integration

The frontend communicates with:
- **Non-streaming**: `POST /api/v1/query`
- **Streaming**: `POST /api/v1/query/stream` (Server-Sent Events)

Both endpoints accept:
```json
{
  "question": "What is the leave policy?",
  "user_id": "user123",
  "top_k": 5
}
```

---

## Production Access

**Live URL**: https://company-project-f3ae.onrender.com

The frontend automatically uses the production backend API.

---

**Last Updated:** May 11, 2026  
**Deployment Status:** ✅ Serving from Render Backend