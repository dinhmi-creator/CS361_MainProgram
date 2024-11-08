import os
import json
import redis
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = 60 * 60  # Cache Time-To-Live: 1 hour

# Initialize Redis client
redis_client = redis.StrictRedis.from_url(REDIS_URL)

def get_from_cache(key):
    """Retrieve data from Redis cache by key."""
    cached_data = redis_client.get(key)
    if cached_data:
        return json.loads(cached_data)  # Convert JSON back to Python dictionary
    return None

def set_in_cache(key, data, ttl=CACHE_TTL):
    """Set data in Redis cache with a specified TTL."""
    redis_client.setex(key, ttl, json.dumps(data))  # Store data as JSON

def delete_from_cache(key):
    """Remove a specific key from the cache."""
    redis_client.delete(key)

def clear_cache():
    """Clear all keys from the cache (use carefully)."""
    redis_client.flushdb()
