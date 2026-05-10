import os
from typing import List, Dict, Any
from pathlib import Path
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader
import docx2txt
import pandas as pd

class DocumentProcessor:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def load_documents(self, directory_path: Path) -> List[Dict[str, Any]]:
        """Load all documents from the policies directory"""
        documents = []
        
        for file_path in directory_path.glob("*"):
            if file_path.suffix.lower() == '.pdf':
                docs = self._load_pdf(file_path)
            elif file_path.suffix.lower() == '.txt':
                docs = self._load_text(file_path)
            elif file_path.suffix.lower() == '.docx':
                docs = self._load_docx(file_path)
            else:
                continue
            
            documents.extend(docs)
        
        return documents
    
    def _load_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load PDF documents"""
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        
        documents = []
        for page in pages:
            metadata = {
                "document_name": file_path.stem,
                "document_type": "pdf",
                "source": str(file_path),
                "page_number": page.metadata.get("page", 0)
            }
            documents.append({
                "content": page.page_content,
                "metadata": metadata
            })
        
        return documents
    
    def _load_text(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load text documents"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return [{
            "content": content,
            "metadata": {
                "document_name": file_path.stem,
                "document_type": "text",
                "source": str(file_path)
            }
        }]
    
    def _load_docx(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load DOCX documents"""
        content = docx2txt.process(str(file_path))
        
        return [{
            "content": content,
            "metadata": {
                "document_name": file_path.stem,
                "document_type": "docx",
                "source": str(file_path)
            }
        }]
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split documents into chunks"""
        chunked_docs = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc["content"])
            
            for i, chunk in enumerate(chunks):
                chunked_docs.append({
                    "content": chunk,
                    "metadata": {
                        **doc["metadata"],
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    }
                })
        
        return chunked_docs
    
    def extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from document content"""
        sections = {}
        lines = content.split('\n')
        current_section = "General"
        
        for line in lines:
            if line.strip() and (line.isupper() or line.startswith(('Section', 'Chapter', 'Article'))):
                current_section = line.strip()
                sections[current_section] = ""
            elif current_section in sections:
                sections[current_section] += line + "\n"
        
        return sections