from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    user_id: Optional[str] = None
    top_k: Optional[int] = 5

class RetrievedChunk(BaseModel):
    content: str
    document_name: str
    section: str
    page_number: Optional[int] = None
    relevance_score: float

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[RetrievedChunk]
    is_relevant: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    response_time_ms: float

class DocumentMetadata(BaseModel):
    document_name: str
    document_type: str
    version: str
    effective_date: str
    sections: List[str]
    last_updated: datetime

class QueryLog(BaseModel):
    query_id: str
    user_id: Optional[str]
    question: str
    answer: str
    sources: List[str]
    response_time: float
    timestamp: datetime
    feedback: Optional[str] = None