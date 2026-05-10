# Complete Render Deployment Guide

## Overview
Your AI Policy Assistant is now configured for complete deployment on Render with both frontend and backend served from the same application.

## What's Included
- ✅ **FastAPI Backend** - API endpoints for policy queries
- ✅ **Static Frontend** - HTML/CSS/JS chat interface
- ✅ **Document Processing** - Policy document indexing
- ✅ **Vector Search** - ChromaDB embeddings
- ✅ **LLM Integration** - NVIDIA API responses

## Project Structure
```
├── app/                    # FastAPI backend
├── static/                 # Frontend files
│   ├── index.html         # Chat interface
│   ├── styles.css         # Mahindra branding
│   └── script.js          # API integration
├── data/policies/          # Policy documents
├── requirements.txt        # Python dependencies
└── render.yaml            # Render deployment config
```

## Deployment Steps

### 1. Create Render Service
1. Go to [render.com](https://render.com) and sign in
2. Click "New" → "Web Service"
3. Connect your GitHub repository: `pramodprajapatcse/Company_Project`
4. Configure the service:
   - **Name**: `company-policy-assistant`
   - **Environment**: `Python 3`
   - **Python Version**: set to `3.9.17` if available, or add a root `.python-version` file with `3.9.17`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2. Environment Variables
Add these environment variables in Render dashboard:

```
NVIDIA_API_KEY=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
LLM_PROVIDER=nvidia
NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1
LOCAL_LLM_MODEL=mistral
API_HOST=0.0.0.0
API_PORT=10000
SECRET_KEY=your-secret-key-here-change-this
ALLOWED_USERS=user1@company.com,user2@company.com
LOG_LEVEL=INFO
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
```

### 3. Resource Configuration
- **Instance Type**: At least `Starter` (512 MB RAM minimum)
- **Region**: Choose closest to your users
- **Auto-deploy**: Enable for automatic updates

### 4. Deploy
1. Click "Create Web Service"
2. Wait for initial deployment (may take 10-15 minutes for first build)
3. Your app will be available at: `https://your-service-name.onrender.com`

## Features

### Frontend (/)
- Modern chat interface with Mahindra branding
- Real-time policy queries
- Responsive design for mobile/desktop
- Policy category sidebar
- Quick question tags

### Backend API (/api/v1)
- `POST /query` - Ask policy questions
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## File Structure Details

### Static Files
- `/` → `static/index.html` (main chat interface)
- `/static/styles.css` → CSS styling
- `/static/script.js` → Frontend JavaScript

### API Endpoints
- `/api/v1/query` → Policy question answering
- `/api/v1/health` → Service health check
- `/docs` → FastAPI interactive documentation

## Testing Your Deployment

### Frontend Access
- **URL**: `https://your-service-name.onrender.com`
- **Features**: Chat interface, policy categories, quick questions

### API Testing
```bash
# Health check
curl https://your-service-name.onrender.com/api/v1/health

# Policy query
curl -X POST https://your-service-name.onrender.com/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the leave policy?", "user_id": "test"}'
```

### Manual Testing
1. Open the frontend URL in a browser
2. Try asking: "What is the IT security policy?"
3. Check the API docs at `/docs`

## Troubleshooting

### Build Issues
- **Memory**: If build fails with OOM, upgrade to higher tier
- **Dependencies**: Check `requirements.txt` for conflicts
- **NLTK**: Resources download automatically on startup

### Runtime Issues
- **CORS**: Already configured for all origins
- **API Errors**: Check NVIDIA API key and network connectivity
- **Documents**: Ensure policy files are in `data/policies/`

### Performance
- **Cold Starts**: First request may be slow due to model loading
- **Memory**: Monitor usage and upgrade if needed
- **Caching**: Documents are cached in memory after first load

## Security Notes
- Change the `SECRET_KEY` to a random string
- Update `ALLOWED_USERS` with actual email addresses
- Consider adding authentication for production use

## Updates
- Push changes to GitHub `main` branch
- Render will auto-deploy if enabled
- Monitor logs in Render dashboard for issues

Your complete AI Policy Assistant is now ready for production deployment on Render! 🚀