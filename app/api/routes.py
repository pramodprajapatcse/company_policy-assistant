from fastapi import APIRouter, HTTPException, Depends
from typing import List
import time
import uuid
import traceback
import asyncio
from fastapi.responses import StreamingResponse
from app.models.schemas import QueryRequest, QueryResponse, RetrievedChunk
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.utils.logger import logger
import logging

router = APIRouter()

# Service instances (will be initialized in main)
retrieval_service = None
llm_service = None

def init_services(retrieval, llm):
    global retrieval_service, llm_service
    retrieval_service = retrieval
    llm_service = llm

@router.post("/query", response_model=QueryResponse)
async def query_policy(request: QueryRequest):
    """Process a policy query"""
    start_time = time.time()
    
    try:
        # Generate unique query ID
        query_id = str(uuid.uuid4())
        
        # Check if services are initialized
        if retrieval_service is None or llm_service is None:
            logger.error("Services not initialized")
            raise Exception("Services not initialized. This may happen if documents failed to load during startup.")
        
        # Log incoming query
        logger.info(f"Query {query_id} from user {request.user_id}: {request.question}")
        
        # Check if query is relevant to policy domain
        if not retrieval_service.is_relevant_query(request.question):
            logger.info(f"Query {query_id} rejected - out of domain")
            return QueryResponse(
                question=request.question,
                answer="I'm designed to answer questions about company policies only. Please ask about HR, leave, procurement, travel, safety, IT security, or code of conduct policies.",
                sources=[],
                is_relevant=False,
                response_time_ms=(time.time() - start_time) * 1000
            )
        
        # Retrieve relevant chunks
        top_k = request.top_k or 5
        retrieved_chunks = retrieval_service.hybrid_search(
            request.question,
            top_k=top_k
        )
        
        # If no relevant chunks found
        if not retrieved_chunks:
            logger.info(f"Query {query_id} - no relevant policies found")
            return QueryResponse(
                question=request.question,
                answer="Requested information is not available in official policy documents.",
                sources=[],
                is_relevant=True,
                response_time_ms=(time.time() - start_time) * 1000
            )
        
        # Generate response using LLM
        answer = llm_service.generate_response(
            request.question,
            retrieved_chunks
        )
        
        # Format sources
        sources = [
            RetrievedChunk(
                content=chunk["content"],
                document_name=chunk["metadata"].get("document_name", "Unknown"),
                section=chunk["metadata"].get("section", "General"),
                page_number=chunk["metadata"].get("page_number"),
                relevance_score=chunk.get("score", 0.0)
            )
            for chunk in retrieved_chunks
        ]
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Log response
        logger.info(f"Query {query_id} completed in {response_time_ms:.2f}ms")
        
        return QueryResponse(
            question=request.question,
            answer=answer,
            sources=sources,
            is_relevant=True,
            response_time_ms=response_time_ms
        )
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing query {query_id}: {str(e)}\n{error_traceback}")
        print(f"[BACKEND ERROR] {str(e)}\n{error_traceback}")  # Also print to stdout for Render logs
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/query/stream")
async def query_policy_stream(request: QueryRequest):
    """Process a policy query with streaming response"""
    start_time = time.time()
    
    try:
        # Generate unique query ID
        query_id = str(uuid.uuid4())
        
        # Check if services are initialized
        if retrieval_service is None or llm_service is None:
            logger.error("Services not initialized")
            raise Exception("Services not initialized. This may happen if documents failed to load during startup.")
        
        # Log incoming query
        logger.info(f"Streaming query {query_id} from user {request.user_id}: {request.question}")
        
        # Check if query is relevant to policy domain
        if not retrieval_service.is_relevant_query(request.question):
            logger.info(f"Query {query_id} rejected - out of domain")
            async def generate_response():
                yield f"data: I'm designed to answer questions about company policies only. Please ask about HR, leave, procurement, travel, safety, IT security, or code of conduct policies.\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(generate_response(), media_type="text/event-stream")
        
        # Retrieve relevant chunks
        top_k = request.top_k or 5
        retrieved_chunks = retrieval_service.hybrid_search(
            request.question,
            top_k=top_k
        )
        
        # If no relevant chunks found
        if not retrieved_chunks:
            logger.info(f"Query {query_id} - no relevant policies found")
            async def generate_response():
                yield f"data: Requested information is not available in official policy documents.\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(generate_response(), media_type="text/event-stream")
        
        # Generate streaming response using LLM
        async def generate_response():
            try:
                # Get the full response first (since NVIDIA API doesn't support true streaming)
                answer = llm_service.generate_response(
                    request.question,
                    retrieved_chunks
                )
                
                # Stream the response character by character with small delays
                for i, char in enumerate(answer):
                    yield f"data: {char}\n\n"
                    await asyncio.sleep(0.02)  # Small delay for typing effect
                
                yield "data: [DONE]\n\n"
                
                response_time_ms = (time.time() - start_time) * 1000
                logger.info(f"Streaming query {query_id} completed in {response_time_ms:.2f}ms")
                
            except Exception as e:
                logger.error(f"Error in streaming response: {e}")
                yield f"data: Error: {str(e)}\n\n"
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate_response(), media_type="text/event-stream")
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing streaming query {query_id}: {str(e)}\n{error_traceback}")
        print(f"[BACKEND ERROR] {str(e)}\n{error_traceback}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.get("/documents")
async def list_documents():
    """List available policy documents"""
    # Implement document listing
    return {"documents": []}