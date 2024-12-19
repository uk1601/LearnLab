import os
from typing import Optional, Dict, Any
from agents.utils.upstash_semantic_cache.semantic_cache import SemanticCache
from datetime import datetime
import json

class PodcastCache:
    def __init__(self):
        """Initialize the semantic cache for podcast queries"""
        self.cache = SemanticCache(
            url=os.getenv("UPSTASH_VECTOR_REST_URL"),
            token=os.getenv("UPSTASH_VECTOR_REST_TOKEN"),
            min_proximity=0.97  # Adjust similarity threshold as needed
        )

    def generate_cache_key(self, query: str, pdf_title: str) -> str:
        """Generate a unique cache key for the query-document pair"""
        return f"{pdf_title}:{query}"

    def get_cached_podcast(self, query: str, pdf_title: str) -> Optional[Dict[str, Any]]:
        """
        Try to retrieve a cached podcast for a similar query
        Returns None if no similar query is found
        """
        try:
            cache_key = self.generate_cache_key(query, pdf_title)
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                # Parse the cached string back into a dictionary
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            print(f"Cache retrieval error: {str(e)}")
            return None

    def cache_podcast(self, query: str, pdf_title: str, podcast_data: Dict[str, Any]) -> bool:
        """
        Cache the podcast data for future retrieval
        Returns True if caching was successful
        """
        try:
            cache_key = self.generate_cache_key(query, pdf_title)
            
            # Add timestamp to podcast data
            podcast_data['cached_at'] = datetime.now().isoformat()
            
            # Convert dictionary to string for caching
            cache_value = json.dumps(podcast_data)
            
            self.cache.set(cache_key, cache_value)
            return True
            
        except Exception as e:
            print(f"Cache storage error: {str(e)}")
            return False

    def clear_cache(self) -> bool:
        """Clear all cached entries"""
        try:
            self.cache.flush()
            return True
        except Exception as e:
            print(f"Cache clear error: {str(e)}")
            return False

