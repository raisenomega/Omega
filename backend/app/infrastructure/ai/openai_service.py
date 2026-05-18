"""
OpenAI Service
Handles all interactions with OpenAI API
"""
from typing import List, Optional, Dict, Any
import logging
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o"
        self.image_model = "dall-e-3"
    
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text using GPT-4
        
        Args:
            prompt: User prompt
            system_message: System instructions
            temperature: Creativity (0-2)
            max_tokens: Maximum response length
            
        Returns:
            Generated text
        """
        try:
            messages = []
            
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            text = response.choices[0].message.content
            logger.info(f"Generated text: {len(text)} characters")
            
            return text
            
        except Exception as e:
            logger.error(f"OpenAI text generation error: {e}")
            raise
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1
    ) -> List[str]:
        """
        Generate images using DALL-E 3
        
        Args:
            prompt: Image description
            size: Image size (1024x1024, 1024x1792, 1792x1024)
            quality: Image quality (standard, hd)
            n: Number of images
            
        Returns:
            List of image URLs
        """
        try:
            response = await self.client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            
            urls = [img.url for img in response.data]
            logger.info(f"Generated {len(urls)} images")
            
            return urls
            
        except Exception as e:
            logger.error(f"OpenAI image generation error: {e}")
            raise
    
    async def create_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small"
    ) -> List[List[float]]:
        """
        Create embeddings for semantic search
        
        Args:
            texts: List of texts to embed
            model: Embedding model
            
        Returns:
            List of embedding vectors
        """
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Created {len(embeddings)} embeddings")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"OpenAI embeddings error: {e}")
            raise


# Global instance
openai_service = OpenAIService()
