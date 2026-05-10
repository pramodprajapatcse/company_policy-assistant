from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api import routes
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.config import config
from app.utils.logger import setup_logging
from app.api.auth_routes import router as auth_router
import logging
import nltk

# Download required NLTK data for tokenization
for resource in ['tokenizers/punkt', 'tokenizers/punkt_tab']:
    try:
        nltk.data.find(resource)
    except LookupError:
        resource_name = resource.split('/')[-1]
        nltk.download(resource_name, quiet=True)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Company Policy RAG Assistant",
    description="AI-powered assistant for company policy queries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
embedding_service = EmbeddingService()
retrieval_service = RetrievalService(embedding_service)
llm_service = LLMService()

# Initialize routes with services
routes.init_services(retrieval_service, llm_service)

# Include routers
app.include_router(routes.router, prefix="/api/v1", tags=["policy"])
app.include_router(auth_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Load documents on startup with memory optimization"""
    import gc
    
    logger.info(" Starting up RAG Assistant...")

    try:
        # Initialize processor
        processor = DocumentProcessor(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )

        # Load documents
        documents = processor.load_documents(config.POLICIES_DIR)
        logger.info(f" Loaded {len(documents)} documents")

        # ❗ SAFETY CHECK: No documents
        if not documents:
            logger.warning(" No documents found in policies directory")
            return

        # Chunk documents
        chunked_docs = processor.chunk_documents(documents)
        logger.info(f" Created {len(chunked_docs)} chunks")

        # ❗ CRITICAL FIX: Prevent empty chunk crash
        if not chunked_docs:
            logger.error(" No chunks created — check document content or chunking logic")
            return

        # Cleanup temporary data before indexing
        del documents
        gc.collect()
        logger.info(" Memory cleanup after chunking")

        # Add to vector DB with batching
        embedding_service.add_documents(chunked_docs, batch_size=10)
        logger.info(" Added chunks to vector database")
        gc.collect()

        # Build BM25 index
        retrieval_service.build_bm25_index(chunked_docs)
        logger.info(" BM25 index built successfully")
        gc.collect()

        # Cleanup
        del chunked_docs
        gc.collect()
        
        logger.info(" Document indexing completed successfully")

    except Exception as e:
        logger.exception(f" Error during startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(" Shutting down RAG Assistant...")


@app.get("/")
async def root():
    return {
        "message": "Company Policy RAG Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )