import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self._memory_cache = {}
        self._cache_ttl = 3600  # 1 hour in seconds

    def _is_expired(self, timestamp: datetime) -> bool:
        return datetime.utcnow() - timestamp > timedelta(seconds=self._cache_ttl)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            cache_ttl = ttl or self._cache_ttl
            expiry_time = datetime.utcnow() + timedelta(seconds=cache_ttl)
            
            self._memory_cache[key] = {
                'value': value,
                'expiry': expiry_time,
                'created_at': datetime.utcnow()
            }
            
            logger.debug(f"Cached {key} with TTL {cache_ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache for {key}: {str(e)}")
            return False

    def get(self, key: str) -> Optional[Any]:
        try:
            if key not in self._memory_cache:
                return None
            
            cache_entry = self._memory_cache[key]
            
            if datetime.utcnow() > cache_entry['expiry']:
                del self._memory_cache[key]
                logger.debug(f"Cache expired for {key}")
                return None
            
            logger.debug(f"Cache hit for {key}")
            return cache_entry['value']
            
        except Exception as e:
            logger.error(f"Error getting cache for {key}: {str(e)}")
            return None

    def delete(self, key: str) -> bool:
        try:
            if key in self._memory_cache:
                del self._memory_cache[key]
                logger.debug(f"Deleted cache for {key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting cache for {key}: {str(e)}")
            return False

    def clear(self) -> bool:
        try:
            self._memory_cache.clear()
            logger.info("Cleared all cache entries")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        now = datetime.utcnow()
        active_entries = 0
        expired_entries = 0
        
        for key, entry in self._memory_cache.items():
            if now > entry['expiry']:
                expired_entries += 1
            else:
                active_entries += 1
        
        return {
            'total_entries': len(self._memory_cache),
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'cache_ttl': self._cache_ttl
        }