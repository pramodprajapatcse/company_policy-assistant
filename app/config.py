import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    POLICIES_DIR = DATA_DIR / "policies"
    PROCESSED_DIR = DATA_DIR / "processed"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Ensure directories exist
    for dir_path in [DATA_DIR, POLICIES_DIR, PROCESSED_DIR, LOGS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Embedding settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DEVICE = "cpu"
    
    # Chunking settings
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    # Retrieval settings
    TOP_K_RESULTS = 5
    VECTOR_SEARCH_WEIGHT = 0.7
    BM25_SEARCH_WEIGHT = 0.3
    
    # LLM settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "nvidia").lower()  # nvidia or local
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_API_BASE_URL = os.getenv("NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_LLM_MODEL = os.getenv("NVIDIA_LLM_MODEL", "meta/llama-4-maverick-17b-128e-instruct")
    LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "mistral")
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALLOWED_USERS = os.getenv("ALLOWED_USERS", "").split(",")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / "rag_assistant.log"
    
    # Vector DB settings
    VECTOR_DB_PATH = PROCESSED_DIR / "chroma_db"
    
    # Domain rejection
    POLICY_DOMAINS = [
        "hr", "leave", "attendance", "procurement", "travel", 
        "reimbursement", "safety", "compliance", "it", "security", 
        "code of conduct", "policy", "employee", "benefits"
    ]

config = Config()