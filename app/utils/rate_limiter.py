"""
Rate Limiting Utilities
"""

import time
import functools
from collections import defaultdict, deque
from flask import request, jsonify
from app.core.config import Config

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.config = Config()
    
    def is_allowed(self, key: str, requests_per_minute: int) -> bool:
        """Check if request is allowed"""
        if not self.config.RATE_LIMIT_ENABLED:
            return True
        
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        while self.requests[key] and self.requests[key][0] < minute_ago:
            self.requests[key].popleft()
        
        # Check if limit exceeded
        if len(self.requests[key]) >= requests_per_minute:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key: str, requests_per_minute: int) -> int:
        """Get remaining requests for the current minute"""
        if not self.config.RATE_LIMIT_ENABLED:
            return requests_per_minute
        
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        while self.requests[key] and self.requests[key][0] < minute_ago:
            self.requests[key].popleft()
        
        return max(0, requests_per_minute - len(self.requests[key]))

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(requests_per_minute: int = None):
    """Rate limiting decorator"""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Use provided limit or default from config
            limit = requests_per_minute or Config().RATE_LIMIT_PER_MINUTE
            
            # Get client identifier (IP address)
            client_id = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # Check rate limit
            if not rate_limiter.is_allowed(client_id, limit):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {limit} requests per minute allowed'
                }), 429
            
            # Add rate limit headers
            remaining = rate_limiter.get_remaining(client_id, limit)
            response = f(*args, **kwargs)
            
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Reset'] = str(int(time.time() + 60))
            
            return response
        return wrapper
    return decorator