"""ML Service for embeddings and semantic search"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class MLService:
    """Service for ML operations: embedding generation and similarity search"""
    
    def __init__(self):
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model"""
        if self._model is None:
            try:
                logger.info(f"Loading embedding model: {settings.embedding_model}")
                self._model = SentenceTransformer(
                    settings.embedding_model,
                    cache_folder=settings.embedding_cache_dir
                )
                logger.info("✅ Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load embedding model: {e}")
                raise
        return self._model
    
    def create_embedding_text(self, issue_data: dict) -> str:
        """
        Create composite text from issue data for embedding generation
        
        Args:
            issue_data: Dictionary with issue fields
            
        Returns:
            Composite text string
        """
        components = [
            f"Error Type: {issue_data.get('error_type', '')}",
            f"Message: {issue_data.get('error_message', '')}"
        ]
        
        # Add stack trace (top 5 lines only)
        if issue_data.get('stack_trace'):
            stack_lines = issue_data['stack_trace'].split('\n')[:5]
            components.append(f"Stack: {' '.join(stack_lines)}")
        
        # Add tags
        if issue_data.get('tags'):
            components.append(f"Tags: {', '.join(issue_data['tags'])}")
        
        # Add language
        if issue_data.get('language'):
            components.append(f"Language: {issue_data['language']}")
        
        # Add framework
        if issue_data.get('framework'):
            components.append(f"Framework: {issue_data['framework']}")
        
        return " | ".join(components)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for given text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            # Validate and clean input
            if not text or not isinstance(text, str):
                logger.warning("Empty or invalid text for embedding, using default")
                text = "Empty error"
            
            # Trim very long text to avoid memory issues
            if len(text) > 5000:
                logger.info(f"Trimming long text from {len(text)} to 5000 chars")
                text = text[:5000]
            
            # Generate embedding with proper string input
            embedding = self.model.encode(
                str(text).strip(),
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            # Return a zero vector as fallback (384 dimensions for MiniLM)
            logger.warning("Returning zero vector as fallback")
            return [0.0] * 384
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings
        Handles both float arrays and string representations
        """
        try:
            # Convert from string if needed (Supabase stores as text)
            if isinstance(embedding1, str):
                import json
                embedding1 = json.loads(embedding1)
            if isinstance(embedding2, str):
                import json
                embedding2 = json.loads(embedding2)
            
            # Ensure we have float arrays
            vec1 = np.array(embedding1, dtype=np.float32)
            vec2 = np.array(embedding2, dtype=np.float32)
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"❌ Failed to compute similarity: {e}")
            return 0.0


# Global ML service instance
ml_service = MLService()


def get_ml_service() -> MLService:
    """Dependency for getting ML service"""
    return ml_service
