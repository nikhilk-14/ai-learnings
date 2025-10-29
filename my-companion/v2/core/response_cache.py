"""
Response Cache - Simple caching system for LLM responses
Reduces repeated LLM calls for similar queries to improve speed.
"""
import hashlib
import json
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class CacheEntry:
    """Cache entry with response and metadata"""
    response: str
    query_type: str
    timestamp: float
    hit_count: int = 0


class ResponseCache:
    """
    Simple in-memory response cache for LLM queries
    Features:
    - Query similarity detection using hashing
    - Time-based expiry
    - Selective caching based on query type
    """
    
    def __init__(self, max_cache_size: int = 100, cache_ttl_hours: int = 24):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl_hours * 3600  # Convert to seconds
        
        # Query types that benefit from caching
        self.cacheable_types = {
            'profile_analysis', 'career_suggestions', 'project_ideas', 
            'skill_analysis', 'technical_question', 'project_specific_question',
            'general_question'  # Added common AI Assistant query types
        }
        
        # Keywords that make queries less cacheable (too specific) - made more restrictive
        self.non_cacheable_keywords = {
            'today', 'now', 'latest news', 'recent update', 'right now', 'this moment'
        }
    
    def _generate_cache_key(self, question: str, query_type: str, context_summary: str = "") -> str:
        """Generate cache key from question and context"""
        # Normalize question for better matching
        normalized_question = self._normalize_question(question)
        
        # Include query type and context summary for more accurate caching
        cache_input = f"{query_type}:{normalized_question}:{context_summary}"
        
        # Generate hash
        return hashlib.md5(cache_input.encode()).hexdigest()[:16]
    
    def _normalize_question(self, question: str) -> str:
        """Normalize question for better cache matching"""
        # Convert to lowercase and remove extra spaces
        question = question.lower().strip()
        
        # Remove common variations that don't change the core question
        replacements = {
            'can you ': '',
            'could you ': '',
            'please ': '',
            'would you ': '',
            '?': '',
            '.': '',
            'my ': '',
            'the ': '',
            'a ': '',
            'an ': ''
        }
        
        for old, new in replacements.items():
            question = question.replace(old, new)
        
        # Remove extra spaces
        question = ' '.join(question.split())
        
        return question
    
    def _is_cacheable(self, question: str, query_type: str) -> bool:
        """Determine if a query should be cached"""
        # Check if query type is cacheable
        if query_type not in self.cacheable_types:
            return False
        
        # Special handling for general_question - only cache if it's profile-related
        if query_type == 'general_question':
            profile_keywords = ['profile', 'experience', 'skills', 'project', 'work', 'background', 'about me', 'my']
            if not any(keyword in question.lower() for keyword in profile_keywords):
                return False
        
        # Check for non-cacheable keywords
        question_lower = question.lower()
        if any(keyword in question_lower for keyword in self.non_cacheable_keywords):
            return False
        
        # Don't cache very short or very long questions
        question_len = len(question.strip())
        if question_len < 10 or question_len > 500:
            return False
        
        return True
    
    def _is_cache_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid"""
        current_time = time.time()
        return (current_time - entry.timestamp) < self.cache_ttl
    
    def _cleanup_cache(self):
        """Remove expired entries and maintain cache size"""
        current_time = time.time()
        
        # Remove expired entries
        expired_keys = [
            key for key, entry in self.cache.items()
            if (current_time - entry.timestamp) > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        # If still over limit, remove least recently used entries
        if len(self.cache) > self.max_cache_size:
            # Sort by timestamp (oldest first)
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].timestamp
            )
            
            # Remove oldest entries
            entries_to_remove = len(self.cache) - self.max_cache_size
            for key, _ in sorted_entries[:entries_to_remove]:
                del self.cache[key]
    
    def get_cached_response(self, question: str, query_type: str, context_summary: str = "") -> Optional[str]:
        """
        Get cached response if available and valid
        
        Args:
            question: User's question
            query_type: Type of query (from PromptTemplates.detect_query_type)
            context_summary: Summary of context for cache key generation
            
        Returns:
            Cached response string or None if not found/expired
        """
        if not self._is_cacheable(question, query_type):
            return None
        
        cache_key = self._generate_cache_key(question, query_type, context_summary)
        
        if cache_key not in self.cache:
            return None
        
        entry = self.cache[cache_key]
        
        if not self._is_cache_entry_valid(entry):
            # Remove expired entry
            del self.cache[cache_key]
            return None
        
        # Update hit count and return response
        entry.hit_count += 1
        return entry.response
    
    def cache_response(self, question: str, query_type: str, response: str, context_summary: str = ""):
        """
        Cache a response for future use
        
        Args:
            question: User's question
            query_type: Type of query
            response: LLM response to cache
            context_summary: Summary of context used
        """
        if not self._is_cacheable(question, query_type):
            return
        
        # Don't cache error responses or very short responses
        if len(response.strip()) < 20 or "error" in response.lower() or response.lower().startswith("sorry"):
            return
        
        cache_key = self._generate_cache_key(question, query_type, context_summary)
        
        # Create cache entry
        entry = CacheEntry(
            response=response,
            query_type=query_type,
            timestamp=time.time(),
            hit_count=0
        )
        
        self.cache[cache_key] = entry
        
        # Cleanup cache if needed
        self._cleanup_cache()
    
    def _generate_context_summary(self, context: Dict[str, str]) -> str:
        """Generate a short summary of context for cache key"""
        # Create a short hash of the context for cache key
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()[:8]
    
    def invalidate_cache(self):
        """Clear all cached responses (e.g., when profile data changes)"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache:
            return {
                "total_entries": 0,
                "cache_hit_rate": 0,
                "most_popular_query_type": "None",
                "cache_size_mb": 0
            }
        
        # Calculate total hits
        total_hits = sum(entry.hit_count for entry in self.cache.values())
        total_entries = len(self.cache)
        
        # Find most popular query type
        query_type_counts = {}
        for entry in self.cache.values():
            query_type_counts[entry.query_type] = query_type_counts.get(entry.query_type, 0) + 1
        
        most_popular = max(query_type_counts.items(), key=lambda x: x[1])[0] if query_type_counts else "None"
        
        # Estimate cache size
        cache_size_bytes = sum(len(entry.response.encode('utf-8')) for entry in self.cache.values())
        cache_size_mb = cache_size_bytes / (1024 * 1024)
        
        return {
            "total_entries": total_entries,
            "total_hits": total_hits,
            "average_hits_per_entry": total_hits / total_entries if total_entries > 0 else 0,
            "most_popular_query_type": most_popular,
            "cache_size_mb": round(cache_size_mb, 2),
            "query_type_distribution": query_type_counts
        }