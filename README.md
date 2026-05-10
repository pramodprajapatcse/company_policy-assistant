# 🏭 Mahindra Rise - AI Policy Assistant

**Live Deployment**: https://company-project-f3ae.onrender.com

An intelligent AI-powered chatbot that helps employees find answers to questions about company policies using natural language processing and vector search.

---

## 📋 Features

✨ **Core Features:**
- 🤖 AI-powered conversational assistant for policy queries
- 📚 100+ indexed company policy documents (HR, IT Security, Procurement, Travel, Safety, Code of Conduct)
- 🔍 Hybrid search combining vector similarity + BM25 keyword matching
- 💬 Real-time streaming responses with ChatGPT-like typing effect
- 🎨 Responsive web interface with Mahindra branding
- 📊 Query logging and performance monitoring

✅ **Technical Features:**
- FastAPI backend with async/await support
- NVIDIA API integration for LLM responses (no OpenAI costs)
- ChromaDB vector database for semantic search
- Sentence-transformers for embeddings
- Docker containerization for consistent deployment
- Stream-based responses for better UX

---

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/pramodprajapatcse/Company_Project.git
cd company-policy-rag

# Configure Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export NVIDIA_API_KEY=your_nvidia_api_key_here

# Run the application
python -m uvicorn app.main:app --reload

# Visit http://localhost:8000
```

### Docker

```bash
# Build the image
docker build -f docker/Dockerfile -t company-policy-assistant .

# Run the container
docker run -e NVIDIA_API_KEY=your_key -p 8000:8000 company-policy-assistant
```

---

## 📁 Project Structure

```
company-policy-rag/
├── app/
│   ├── main.py                 # FastAPI application setup
│   ├── config.py               # Configuration and environment variables
│   ├── api/
│   │   ├── routes.py          # Query endpoints (/api/v1/query, /api/v1/query/stream)
│   │   └── auth_routes.py     # Authentication endpoints
│   ├── services/
│   │   ├── document_processor.py       # Parse policy documents
│   │   ├── embedding_service.py        # Vector embeddings via ChromaDB
│   │   ├── retrieval_service.py        # Hybrid search (vector + BM25)
│   │   ├── llm_service.py              # NVIDIA LLM integration
│   │   └── user_service.py             # User management
│   ├── models/
│   │   ├── document.py         # Document schema
│   │   ├── schemas.py          # API request/response schemas
│   │   └── user.py             # User schema
│   └── utils/
│       ├── logger.py           # Structured logging
│       └── security.py         # Security utilities
├── static/
│   ├── index.html              # Chat UI
│   ├── styles.css              # Styling (Mahindra branding)
│   ├── script.js               # Frontend logic & streaming
│   └── MAHINDRALOGO.jpeg       # Company logo
├── data/
│   ├── policies/               # Policy documents (100+ indexed)
│   ├── processed/
│   │   └── chroma_db/          # Vector database storage
│   └── users.json              # User data
├── docker/
│   ├── Dockerfile              # Production Docker image
│   └── docker-compose.yml      # Local development setup
├── requirements.txt            # Python dependencies
├── Procfile                    # Render start command
├── render.yaml                 # Render service configuration
└── .python-version             # Python 3.9.17 pin
```

---

## 🔧 API Endpoints

### Query Endpoints

**POST** `/api/v1/query` - Non-streaming response
```bash
curl -X POST https://company-project-f3ae.onrender.com/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the leave policy?",
    "user_id": "user123",
    "top_k": 5
  }'
```

**POST** `/api/v1/query/stream` - Streaming response (Server-Sent Events)
```bash
curl -X POST https://company-project-f3ae.onrender.com/api/v1/query/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are IT security guidelines?",
    "user_id": "user123",
    "top_k": 5
  }'
```

**GET** `/api/v1/health` - Health check
```bash
curl https://company-project-f3ae.onrender.com/api/v1/health
```

### Response Format

```json
{
  "answer": "Here is information about the leave policy...",
  "sources": [
    {
      "content": "...",
      "document_name": "HR Policies",
      "section": "Leave Attendance",
      "page_number": 1,
      "relevance_score": 0.92
    }
  ],
  "is_relevant": true,
  "response_time_ms": 2341.56
}
```

---

## 📊 Monitoring & Logging

### View Logs on Render
1. Go to https://render.com
2. Select **company-policy-assistant** service
3. Click **Logs** tab
4. See real-time application logs

### Browser Console
- Press **F12** → **Console** tab
- See frontend API calls and responses
- Check for errors or performance issues

### Health Monitoring
```bash
# Check if service is alive
curl https://company-project-f3ae.onrender.com/api/v1/health

# Response: {"status": "healthy"}
```

### Log Files (Local)
```bash
tail -f logs/app.log
```

---

## 🔐 Configuration

### Environment Variables (Render)
Set in Render dashboard → Settings → Environment Variables:
- `NVIDIA_API_KEY` - Your NVIDIA API key for LLM responses
- `LOG_LEVEL` - (Optional) Logging level (default: INFO)

### Local .env File
```env
NVIDIA_API_KEY=your_nvidia_api_key_here
LOG_LEVEL=INFO
```

---

## 📦 Technology Stack

**Backend:**
- Python 3.9.17
- FastAPI 0.104.1
- Uvicorn 0.24.0
- PyTorch 2.8.0 (CPU)
- ChromaDB 0.4.22
- Sentence-transformers 3.0.0
- Rank-BM25 0.2.2
- OpenAI client (for NVIDIA API)

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Server-Sent Events (streaming)
- Font Awesome icons
- Responsive design

**Deployment:**
- Docker (containerization)
- Render (hosting)
- Python 3.9.17 (runtime)

---

## 🚢 Deployment on Render

### Prerequisites
- GitHub repository (push code here)
- Render account (https://render.com)
- NVIDIA API key (free tier available)

### Deployment Steps

1. **Connect GitHub**
   - Go to https://render.com/dashboard
   - Click **New** → **Web Service**
   - Connect your GitHub repository

2. **Configure Service**
   - **Name:** company-policy-assistant
   - **Runtime:** Docker
   - **Build Command:** `docker build -f docker/Dockerfile .`
   - **Port:** 8000

3. **Environment Variables**
   - Add `NVIDIA_API_KEY` from your NVIDIA account

4. **Deploy**
   - Click **Create Web Service**
   - Render will auto-deploy on every GitHub push

### Auto-Deployment
Changes are automatically deployed when you push to the `main` branch:
```bash
git add .
git commit -m "Your message"
git push origin main
```

---

## 📈 Performance Metrics

**Typical Response Times:**
- Vector search: 150-300ms
- BM25 search: 50-100ms
- LLM response generation: 2000-3000ms
- **Total:** 2-3 seconds per query

**Scalability:**
- 100+ policy documents indexed
- Supports concurrent users
- Streaming responses reduce perceived latency
- Memory optimized with batch processing

---

## 🛠️ Development

### Adding New Policies
1. Add `.txt` file to `data/policies/`
2. Restart the application
3. Documents are auto-indexed on startup

### Customizing LLM Behavior
Edit `app/services/llm_service.py`:
- Adjust `temperature` for response variability
- Modify `max_tokens` for response length
- Update system prompt for different behaviors

### Frontend Customization
- **Colors:** Edit CSS variables in `static/styles.css`
- **Questions:** Update tags in `static/index.html`
- **Logo:** Replace `static/MAHINDRALOGO.jpeg`

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| API returns 500 error | Check NVIDIA_API_KEY in Render settings |
| Streaming not working | Verify `/api/v1/query/stream` endpoint exists |
| Documents not loading | Check `data/policies/` folder has files |
| Slow responses | Check LLM model availability on NVIDIA |
| Logo not showing | Verify `static/MAHINDRALOGO.jpeg` exists |

---

## 📝 License

This project is proprietary to Mahindra.

---

## 👥 Support

For issues or questions:
1. Check the logs on Render dashboard
2. Review browser console (F12)
3. Test API endpoints directly with curl

---

**Last Updated:** May 11, 2026  
**Deployment Status:** ✅ Live on Render  
**Live URL:** https://company-project-f3ae.onrender.com
