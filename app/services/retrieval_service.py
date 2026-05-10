from typing import List, Dict, Any
import numpy as np
from rank_bm25 import BM25Okapi
import re
from app.services.embedding_service import EmbeddingService
from app.config import config
import logging

logger = logging.getLogger(__name__)


def _simple_word_tokenize(text: str) -> List[str]:
    """Simple word tokenizer fallback that doesn't require NLTK punkt"""
    # Convert to lowercase and split on non-alphanumeric characters
    text = text.lower()
    # Split on whitespace and punctuation
    words = re.findall(r"\b[a-z0-9]+\b", text)
    return words

class RetrievalService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.bm25_index = None
        self.documents = []
        self.tokenized_docs = []
        
    def build_bm25_index(self, documents: List[Dict[str, Any]]):
        """Build BM25 index for keyword search with memory optimization"""
        import gc
        
        self.documents = documents
        self.tokenized_docs = []
        
        # Tokenize documents in a memory-efficient way
        for i, doc in enumerate(documents):
            # Use simple tokenizer to avoid NLTK punkt_tab dependency issues
            self.tokenized_docs.append(_simple_word_tokenize(doc["content"]))
            # Periodic cleanup to avoid memory buildup during tokenization
            if (i + 1) % 20 == 0:
                gc.collect()
        
        self.bm25_index = BM25Okapi(self.tokenized_docs)
        logger.info(f"Built BM25 index with {len(documents)} documents")
        gc.collect()
    
    def bm25_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform BM25 keyword search"""
        if not self.bm25_index:
            return []
        
        tokenized_query = _simple_word_tokenize(query.lower())
        scores = self.bm25_index.get_scores(tokenized_query)
        
        # Get top k indices
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    "content": self.documents[idx]["content"],
                    "metadata": self.documents[idx]["metadata"],
                    "score": scores[idx] / max(scores) if max(scores) > 0 else 0
                })
        
        return results
    
    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Combine vector search and BM25 search"""
        try:
            logger.info(f"Hybrid search for query: {query}")
            
            # Vector search
            vector_results = self.embedding_service.search(query, top_k)
            logger.info(f"Vector search returned {len(vector_results)} results")
            
            # BM25 search
            bm25_results = self.bm25_search(query, top_k)
            logger.info(f"BM25 search returned {len(bm25_results)} results")
            
            # Combine results with weights
            combined_scores = {}
            
            for result in vector_results:
                doc_id = result["metadata"].get("chunk_id", hash(result["content"]))
                combined_scores[doc_id] = {
                    "result": result,
                    "score": result["score"] * config.VECTOR_SEARCH_WEIGHT
                }
            
            for result in bm25_results:
                doc_id = result["metadata"].get("chunk_id", hash(result["content"]))
                if doc_id in combined_scores:
                    combined_scores[doc_id]["score"] += result["score"] * config.BM25_SEARCH_WEIGHT
                else:
                    combined_scores[doc_id] = {
                        "result": result,
                        "score": result["score"] * config.BM25_SEARCH_WEIGHT
                    }
            
            # Sort by combined score and return top k
            sorted_results = sorted(
                combined_scores.values(),
                key=lambda x: x["score"],
                reverse=True
            )[:top_k]
            
            logger.info(f"Hybrid search returning {len(sorted_results)} combined results")
            return [item["result"] for item in sorted_results]
        except Exception as e:
            logger.error(f"Error in hybrid_search: {e}", exc_info=True)
            raise
    
    def is_relevant_query(self, query: str) -> bool:
        """Check if query is relevant to policy domain"""
        query_lower = query.lower()
        
        # Check if query contains policy domain keywords
        for domain in config.POLICY_DOMAINS:
            if domain in query_lower:
                return True
        
        # If no domain keywords found, check BM25 relevance
        if self.bm25_index:
            tokenized_query = _simple_word_tokenize(query_lower)
            scores = self.bm25_index.get_scores(tokenized_query)
            if max(scores) > 0:
                return True
        
        return False