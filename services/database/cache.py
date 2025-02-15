# Caching logic with Redis
import redis
import json

class CacheManager:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
    
    def set_data(self, key, value, expiry=None):
        serialized = json.dumps(value)
        self.redis_client.set(key, serialized, ex=expiry)
    
    def get_data(self, key):
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    def delete_data(self, key):
        return self.redis_client.delete(key)
