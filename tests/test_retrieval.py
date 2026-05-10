import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService

class TestRetrieval:
    
    @pytest.fixture
    def setup_services(self):
        """Setup services for testing"""
        processor = DocumentProcessor(chunk_size=200, chunk_overlap=20)
        embedding_service = EmbeddingService()
        retrieval_service = RetrievalService(embedding_service)
        
        return {
            'processor': processor,
            'embedding_service': embedding_service,
            'retrieval_service': retrieval_service
        }
    
    def test_document_loading(self, setup_services):
        """Test document loading"""
        processor = setup_services['processor']
        docs = processor.load_documents(Path("data/policies"))
        
        assert len(docs) > 0
        assert all('content' in doc for doc in docs)
        assert all('metadata' in doc for doc in docs)
    
    def test_chunking(self, setup_services):
        """Test document chunking"""
        processor = setup_services['processor']
        
        test_doc = [{
            'content': 'This is a test document. ' * 100,
            'metadata': {'document_name': 'test'}
        }]
        
        chunks = processor.chunk_documents(test_doc)
        assert len(chunks) > 1
        assert all('content' in chunk for chunk in chunks)
    
    def test_hybrid_search(self, setup_services):
        """Test hybrid search functionality"""
        retrieval_service = setup_services['retrieval_service']
        
        # Add test documents
        test_docs = [
            {
                'content': 'Employees get 20 days of annual leave per year',
                'metadata': {'document_name': 'leave_policy', 'section': 'Leave Policy'}
            },
            {
                'content': 'Sick leave requires medical certificate',
                'metadata': {'document_name': 'leave_policy', 'section': 'Sick Leave'}
            }
        ]
        
        retrieval_service.build_bm25_index(test_docs)
        
        # Test search
        results = retrieval_service.hybrid_search("How many leave days?", top_k=2)
        assert len(results) > 0
        
        # Test relevance check
        is_relevant = retrieval_service.is_relevant_query("What is the leave policy?")
        assert is_relevant == True
        
        is_relevant = retrieval_service.is_relevant_query("What's the weather today?")
        assert is_relevant == False

if __name__ == "__main__":
    pytest.main([__file__])