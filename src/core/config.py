"""
Configuration Management for Muvera
Centralized configuration with environment variable support
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

@dataclass
class VespaConfig:
    """Vespa configuration"""
    endpoint: str = "http://localhost:8080"
    document_api: str = "http://localhost:8080/document/v1"
    search_api: str = "http://localhost:8080/search/"
    timeout: int = 30
    
    @classmethod
    def from_env(cls) -> 'VespaConfig':
        return cls(
            endpoint=os.getenv("VESPA_ENDPOINT", cls.endpoint),
            document_api=os.getenv("VESPA_DOCUMENT_API", cls.document_api),
            search_api=os.getenv("VESPA_SEARCH_API", cls.search_api),
            timeout=int(os.getenv("VESPA_TIMEOUT", cls.timeout))
        )

@dataclass
class DatasetConfig:
    """Dataset configuration"""
    name: str = "msmarco"
    max_passages: int = 100000
    passages_url: str = "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/data/collectionandqueries.tar.gz"
    queries_url: str = "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/data/queries.dev.small.tsv"
    qrels_url: str = "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/data/qrels.dev.small.tsv"
    
    @classmethod
    def from_env(cls) -> 'DatasetConfig':
        return cls(
            max_passages=int(os.getenv("MAX_PASSAGES", cls.max_passages)),
            passages_url=os.getenv("PASSAGES_URL", cls.passages_url),
            queries_url=os.getenv("QUERIES_URL", cls.queries_url),
            qrels_url=os.getenv("QRELS_URL", cls.qrels_url)
        )

@dataclass
class ModelConfig:
    """Model configuration"""
    single_vector_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    single_vector_dimension: int = 384
    multi_vector_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    multi_vector_dimension: int = 128
    max_tokens: int = 512
    batch_size: int = 32
    
    @classmethod
    def from_env(cls) -> 'ModelConfig':
        return cls(
            single_vector_model=os.getenv("SINGLE_VECTOR_MODEL", cls.single_vector_model),
            single_vector_dimension=int(os.getenv("SINGLE_VECTOR_DIMENSION", cls.single_vector_dimension)),
            multi_vector_model=os.getenv("MULTI_VECTOR_MODEL", cls.multi_vector_model),
            multi_vector_dimension=int(os.getenv("MULTI_VECTOR_DIMENSION", cls.multi_vector_dimension)),
            max_tokens=int(os.getenv("MAX_TOKENS", cls.max_tokens)),
            batch_size=int(os.getenv("BATCH_SIZE", cls.batch_size))
        )

@dataclass
class EvaluationConfig:
    """Evaluation configuration"""
    metrics: list = field(default_factory=lambda: ["ndcg_cut_10", "map", "recip_rank", "recall_100", "recall_1000"])
    query_batch_size: int = 32
    top_k: int = 1000
    
    @classmethod
    def from_env(cls) -> 'EvaluationConfig':
        return cls(
            query_batch_size=int(os.getenv("QUERY_BATCH_SIZE", cls.query_batch_size)),
            top_k=int(os.getenv("TOP_K", cls.top_k))
        )

@dataclass
class PathConfig:
    """Path configuration"""
    data_dir: str = "./data"
    raw_dir: str = "./data/raw"
    processed_dir: str = "./data/processed"
    embeddings_dir: str = "./data/embeddings"
    logs_dir: str = "./logs"
    
    @classmethod
    def from_env(cls) -> 'PathConfig':
        data_dir = os.getenv("DATA_DIR", cls.data_dir)
        return cls(
            data_dir=data_dir,
            raw_dir=os.getenv("RAW_DIR", f"{data_dir}/raw"),
            processed_dir=os.getenv("PROCESSED_DIR", f"{data_dir}/processed"),
            embeddings_dir=os.getenv("EMBEDDINGS_DIR", f"{data_dir}/embeddings"),
            logs_dir=os.getenv("LOGS_DIR", cls.logs_dir)
        )

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file: str = "logs/muvera.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        return cls(
            level=os.getenv("LOG_LEVEL", cls.level),
            file=os.getenv("LOG_FILE", cls.file),
            format=os.getenv("LOG_FORMAT", cls.format)
        )

class MuveraConfig:
    """Main configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/default.yaml"
        self._config_data = {}
        self._load_config()
        
        # Initialize sub-configurations
        self.vespa = VespaConfig.from_env()
        self.dataset = DatasetConfig.from_env()
        self.model = ModelConfig.from_env()
        self.evaluation = EvaluationConfig.from_env()
        self.paths = PathConfig.from_env()
        self.logging = LoggingConfig.from_env()
        
        # Create directories
        self._create_directories()
        
        # Setup logging
        self._setup_logging()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        config_path = Path(self.config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                self._config_data = yaml.safe_load(f) or {}
    
    def _create_directories(self):
        """Create necessary directories"""
        dirs_to_create = [
            self.paths.data_dir,
            self.paths.raw_dir,
            self.paths.processed_dir,
            self.paths.embeddings_dir,
            self.paths.logs_dir
        ]
        
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.logging.level),
            format=self.logging.format,
            handlers=[
                logging.FileHandler(self.logging.file),
                logging.StreamHandler()
            ]
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self._config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def save_config(self, output_file: Optional[str] = None):
        """Save current configuration to file"""
        output_file = output_file or self.config_file
        
        config_data = {
            'vespa': {
                'endpoint': self.vespa.endpoint,
                'document_api': self.vespa.document_api,
                'search_api': self.vespa.search_api,
                'timeout': self.vespa.timeout
            },
            'dataset': {
                'name': self.dataset.name,
                'max_passages': self.dataset.max_passages,
                'passages_url': self.dataset.passages_url,
                'queries_url': self.dataset.queries_url,
                'qrels_url': self.dataset.qrels_url
            },
            'model': {
                'single_vector_model': self.model.single_vector_model,
                'single_vector_dimension': self.model.single_vector_dimension,
                'multi_vector_model': self.model.multi_vector_model,
                'multi_vector_dimension': self.model.multi_vector_dimension,
                'max_tokens': self.model.max_tokens,
                'batch_size': self.model.batch_size
            },
            'evaluation': {
                'metrics': self.evaluation.metrics,
                'query_batch_size': self.evaluation.query_batch_size,
                'top_k': self.evaluation.top_k
            },
            'paths': {
                'data_dir': self.paths.data_dir,
                'raw_dir': self.paths.raw_dir,
                'processed_dir': self.paths.processed_dir,
                'embeddings_dir': self.paths.embeddings_dir,
                'logs_dir': self.paths.logs_dir
            },
            'logging': {
                'level': self.logging.level,
                'file': self.logging.file,
                'format': self.logging.format
            }
        }
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)

# Global configuration instance
config = MuveraConfig()

def get_config(config_file: Optional[str] = None) -> MuveraConfig:
    """Get configuration instance"""
    if config_file:
        return MuveraConfig(config_file)
    return config