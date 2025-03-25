from typing import List
from langchain_ollama import OllamaEmbeddings

from app.core.config import get_settings

class EmbeddingService:
    def __init__(self, model_name: str = "llama3.2:1b"):
        """
        Initialize the embedding service using the Ollama server.
        
        Args:
            model_name (str): The name of the model to use 
            default is "llama3.1:latest").
            base_url (str): The base URL of the Ollama server.
        """
        settings = get_settings()
        base_url = settings.ollama_url
        self.embeddings = OllamaEmbeddings(
            model=model_name,
            base_url=base_url
        )

    def truncate_text(
        self, text: str,
        max_length: int = 51200
    ) -> str:
        """
        Optionally truncate the text to avoid exceeding the
        model's input limits.
        
        Args:
            text (str): The input text.
            max_length (int): The maximum allowed length
            (can be character-based).
        
        Returns:
            str: The truncated text.
        """
        return text if len(text) <= max_length else text[:max_length]
    
    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for the given text using the Ollama server.
        
        Args:
            text (str): The input text to embed.
        
        Returns:
            list[float]: The embedding vector.
        """
        truncated_text = self.truncate_text(text)
        return await self.embeddings.aembed_query(truncated_text)

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        truncated_texts = [self.truncate_text(text) for text in texts]
        return await self.embeddings.aembed_documents(truncated_texts)
