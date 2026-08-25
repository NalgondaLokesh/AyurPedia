"""
Embedder module for AyurPedia.
Handles text embedding generation using Cohere AI API.
"""

import time
from typing import List
import cohere
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class Embedder:
    """Text embedder using Cohere AI embeddings API."""
    
    def __init__(self, api_key: str, model_name: str = 'embed-english-v3.0') -> None:
        """Initialize Cohere embedder with API key.
        
        Args:
            api_key: Cohere API key
            model_name: Name of the embedding model (default: embed-english-v3.0)
        """
        self.client = cohere.Client(api_key=api_key)
        self.model_name = model_name
        self.embedding_dimension = 1024  # embed-english-v3.0 dimension
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type(Exception)
    )
    def _generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text with retry logic.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
            
        Raises:
            Exception: If embedding generation fails after retries
        """
        try:
            response = self.client.embed(
                texts=[text],
                model=self.model_name,
                input_type="search_document"
            )
            return response.embeddings[0]
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate limit" in error_str.lower() or "quota" in error_str.lower():
                print(f"RATE LIMIT ERROR: {e}")
                print("Please check your Cohere API quota")
            else:
                print(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each as list of floats)
        """
        if not texts:
            return []
        
        embeddings = []
        for i, text in enumerate(texts):
            try:
                embedding = self._generate_single_embedding(text)
                embeddings.append(embedding)
                
                # Print progress for large batches
                if (i + 1) % 10 == 0:
                    print(f"  Generated {i + 1}/{len(texts)} embeddings...")
                    
            except Exception as e:
                print(f"Failed to generate embedding for text {i}: {e}")
                # Append zero vector as fallback
                embeddings.append([0.0] * self.embedding_dimension)
        
        return embeddings
    
    def embed_batch(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        """Process texts in batches to handle rate limits.
        
        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process in each batch (Cohere max is 96)
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        all_embeddings = []
        total_texts = len(texts)
        
        # Cohere API has a max batch size of 96
        cohere_batch_size = min(batch_size, 96)
        
        for i in range(0, total_texts, cohere_batch_size):
            batch = texts[i:i + cohere_batch_size]
            print(f"Processing batch {i//cohere_batch_size + 1}/{(total_texts + cohere_batch_size - 1)//cohere_batch_size}...")
            
            try:
                response = self.client.embed(
                    texts=batch,
                    model=self.model_name,
                    input_type="search_document"
                )
                all_embeddings.extend(response.embeddings)
                
                # Add delay between batches to respect rate limits
                if i + cohere_batch_size < total_texts:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error processing batch {i//cohere_batch_size + 1}: {e}")
                # Add zero vectors for failed batch
                zero_vectors = [[0.0] * self.embedding_dimension] * len(batch)
                all_embeddings.extend(zero_vectors)
        
        return all_embeddings
    
    def get_embedding_dimension(self) -> int:
        """Return the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension (768 for gemini-embedding-001)
        """
        return self.embedding_dimension
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query.
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding vector
        """
        try:
            response = self.client.embed(
                texts=[query],
                model=self.model_name,
                input_type="search_query"
            )
            return response.embeddings[0]
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            raise
    
    def validate_embedding(self, embedding: List[float]) -> bool:
        """Validate that an embedding has the correct dimension.
        
        Args:
            embedding: Embedding vector to validate
            
        Returns:
            True if valid, False otherwise
        """
        return len(embedding) == self.embedding_dimension
    
    def get_stats(self) -> dict:
        """Get statistics about the embedder.
        
        Returns:
            Dictionary with embedder statistics
        """
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dimension,
            'configured': True
        }