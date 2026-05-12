from typing import List
import numpy as np
import posthog
from app.config import config
import logging

logger = logging.getLogger(__name__)

# Safe posthog wrapper for Chroma telemetry compatibility
# Chroma may call posthog.capture(old_style_args), while the installed
# posthog package expects a newer API signature.
_original_posthog_capture = posthog.capture

def _safe_posthog_capture(*args, **kwargs):
    if getattr(posthog, "disabled", False):
        return None
    if len(args) == 1:
        return _original_posthog_capture(*args, **kwargs)
    if len(args) >= 2:
        distinct_id = args[0]
        event_name = args[1]
        properties = args[2] if len(args) >= 3 else kwargs.get("properties", {})
        return _original_posthog_capture(event_name, distinct_id=distinct_id, properties=properties)
    return _original_posthog_capture(*args, **kwargs)

posthog.disabled = True
posthog.capture = _safe_posthog_capture

import chromadb
from chromadb.config import Settings as ChromaSettings


class EmbeddingService:
    def __init__(self):
        self.model = None
        self.vector_dimension = None

        # Disable Chroma telemetry to avoid posthog compatibility errors
        self.client = chromadb.PersistentClient(
            path=str(config.VECTOR_DB_PATH),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Load embedding model
        self.model = self._load_embedding_model()
        if hasattr(self.model, "get_sentence_embedding_dimension"):
            self.vector_dimension = self.model.get_sentence_embedding_dimension()

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="policy_documents",
            metadata={"hnsw:space": "cosine"}
        )

        logger.info("Embedding service initialized successfully")

    def _load_embedding_model(self):
        if config.LLM_PROVIDER.lower() == "nvidia" and config.NVIDIA_API_KEY:
            try:
                from langchain_community.embeddings import OpenAIEmbeddings

                logger.info("Using NVIDIA embeddings via OpenAI-compatible wrapper")
                base_urls = [config.NVIDIA_API_BASE_URL]
                if config.NVIDIA_API_BASE_URL.endswith("/v1"):
                    base_urls.append(config.NVIDIA_API_BASE_URL[:-3])
                else:
                    base_urls.append(config.NVIDIA_API_BASE_URL.rstrip("/") + "/v1")

                last_exc = None
                for url in base_urls:
                    try:
                        model = OpenAIEmbeddings(
                            openai_api_key=config.NVIDIA_API_KEY,
                            openai_api_base=url,
                            model="text-embedding-3-small"
                        )
                        logger.info("NVIDIA embeddings configured with base URL: %s", url)
                        return model
                    except Exception as e:
                        last_exc = e
                        logger.warning("NVIDIA embeddings unavailable at %s: %s", url, e)

                raise last_exc
            except Exception as e:
                logger.warning(
                    "NVIDIA embeddings unavailable or not supported in this environment, falling back to local embeddings: %s",
                    e,
                )

        if config.LLM_PROVIDER.lower() == "nvidia":
            logger.warning(
                "NVIDIA provider requested but NVIDIA_API_KEY is missing or invalid. Using local embeddings instead."
            )

        return self._load_local_model()

    def _load_local_model(self):
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading local sentence-transformers model: {config.EMBEDDING_MODEL}")
        return SentenceTransformer(config.EMBEDDING_MODEL, device=config.EMBEDDING_DEVICE)

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts"""
        if hasattr(self.model, "embed_documents"):
            embeddings = self.model.embed_documents(texts)
            return np.array(embeddings)

        return self.model.encode(texts, convert_to_numpy=True)

    def add_documents(self, documents: List[dict], batch_size: int = 10):
        """Add documents to vector database in batches to reduce memory usage"""
        import gc
        
        try:
            if not documents:
                return

            total_added = 0
            for batch_start in range(0, len(documents), batch_size):
                batch_end = min(batch_start + batch_size, len(documents))
                batch = documents[batch_start:batch_end]

                # Generate unique IDs
                ids = [f"doc_{i}_{hash(doc['content'])}" for i, doc in enumerate(batch)]

                # Extract texts and metadata
                texts = [doc["content"] for doc in batch]
                metadatas = [doc.get("metadata", {}) for doc in batch]

                # Generate embeddings
                try:
                    embeddings = self.generate_embeddings(texts)
                except Exception as e:
                    logger.warning("Embedding generation failed: %s", e)
                    if config.LLM_PROVIDER.lower() == "nvidia":
                        logger.info("Falling back to local embeddings and retrying")
                        self.model = self._load_local_model()
                        embeddings = self.generate_embeddings(texts)
                    else:
                        raise

                # Add to ChromaDB
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                total_added += len(batch)
                logger.info(f"Added batch {batch_start//batch_size + 1}: {len(batch)} documents to vector DB")
                
                # Cleanup batch memory
                del embeddings, texts, metadatas, ids
                gc.collect()
            
            logger.info(f"Completed: {total_added} total documents added to vector DB")

        except Exception as e:
            logger.error(f" Error adding documents: {e}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])[0]

            # Query database
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )

            formatted_results = []

            if results.get("documents"):
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": (
                            1 - results["distances"][0][i]
                            if results.get("distances")
                            else 1.0
                        )
                    })

            return formatted_results

        except Exception as e:
            logger.error(f" Search error: {e}")
            return []

    def delete_collection(self):
        """Delete the collection"""
        try:
            self.client.delete_collection("policy_documents")
            logger.info("🗑️ Collection deleted successfully")
        except Exception as e:
            logger.error(f" Error deleting collection: {e}")