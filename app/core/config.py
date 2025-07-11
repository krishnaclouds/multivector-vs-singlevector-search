"""
Application Configuration
"""

import os
from pathlib import Path

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else ['*']
    
    # Qdrant Configuration
    QDRANT_HOST = os.environ.get('QDRANT_HOST', 'localhost')
    QDRANT_PORT = int(os.environ.get('QDRANT_PORT', '6333'))
    QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"
    QDRANT_API_KEY = os.environ.get('QDRANT_API_KEY')
    
    # Search Configuration
    COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'semantic_search')
    VECTOR_SIZE = int(os.environ.get('VECTOR_SIZE', '384'))
    MAX_RESULTS = int(os.environ.get('MAX_RESULTS', '50'))
    
    # Embedding Model Configuration
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    MODEL_CACHE_DIR = os.environ.get('MODEL_CACHE_DIR', './models')
    
    # Data Configuration
    DATA_DIR = Path(os.environ.get('DATA_DIR', './data'))
    EMBEDDINGS_DIR = DATA_DIR / 'embeddings'
    PROCESSED_DIR = DATA_DIR / 'processed'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', './logs/app.log')
    
    # Performance Configuration
    SEARCH_TIMEOUT = int(os.environ.get('SEARCH_TIMEOUT', '30'))  # seconds
    CACHE_TTL = int(os.environ.get('CACHE_TTL', '300'))  # seconds
    
    # Security Configuration
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Health Check Configuration
    HEALTH_CHECK_ENABLED = os.environ.get('HEALTH_CHECK_ENABLED', 'True').lower() == 'true'
    
    @classmethod
    def init_directories(cls):
        """Initialize required directories"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.EMBEDDINGS_DIR.mkdir(exist_ok=True)
        cls.PROCESSED_DIR.mkdir(exist_ok=True)
        Path('./logs').mkdir(exist_ok=True)
        Path(cls.MODEL_CACHE_DIR).mkdir(exist_ok=True)


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Ensure secret key is set in production
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    QDRANT_HOST = 'localhost'
    QDRANT_PORT = 6334  # Different port for testing
    COLLECTION_NAME = 'test_collection'


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config_map.get(config_name, DevelopmentConfig)