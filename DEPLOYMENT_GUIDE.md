# Company Policy RAG Assistant - Deployment Guide

## Overview
This guide covers deploying the Company Policy RAG Assistant to production platforms.

## Prerequisites
- GitHub repository: https://github.com/pramodprajapatcse/Company_Project
- API Keys: NVIDIA
- Docker knowledge (optional)

## Deployment Options

### Option 1: Render (Recommended - Free Tier Available)
1. Go to https://render.com
2. Sign up/Login with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repo: `pramodprajapatcse/Company_Project`
5. Configure:
   - **Name**: `company-policy-rag`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./docker/Dockerfile` ✅ **Correct**
   - **Root Directory**: Leave empty
6. Add Environment Variables:
   ```
   NVIDIA_API_KEY=your-nvidia-api-key-here
   NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1
   LLM_PROVIDER=nvidia
   SECRET_KEY=your-production-secret-key-here
   ALLOWED_USERS=your-email@company.com
   ```
7. Click "Create Web Service"
8. Wait for deployment (5-10 minutes)

### Option 2: Railway
1. Go to https://railway.app
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as above)
6. Deploy

### Option 3: Fly.io
1. Install Fly CLI: `brew install flyctl`
2. Login: `fly auth login`
3. Launch: `fly launch`
4. Set secrets: `fly secrets set NVIDIA_API_KEY=your-key-here`
5. Deploy: `fly deploy`

## Environment Variables Required
- `NVIDIA_API_KEY`: Your NVIDIA API key
- `NVIDIA_API_BASE_URL`: NVIDIA integration base URL (default: `https://integrate.api.nvidia.com/v1`)
- `LLM_PROVIDER`: Set to `nvidia` or `local`
- `SECRET_KEY`: Random string for JWT tokens
- `ALLOWED_USERS`: Comma-separated list of allowed email addresses

## Post-Deployment
1. Access your deployed app URL
2. Test the authentication with your email
3. Verify policy queries work correctly

## Troubleshooting
- Check logs in your deployment platform
- Ensure all environment variables are set
- Verify Dockerfile path is correct: `./docker/Dockerfile`