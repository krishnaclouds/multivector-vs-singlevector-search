"""
System API Routes
"""

import logging
from flask import Blueprint, jsonify, current_app
from app.utils.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

system_bp = Blueprint('system', __name__)

@system_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        search_service = current_app.search_service
        status = search_service.get_system_status()
        
        # Determine overall health
        overall_healthy = (
            status.get('model_loaded', False) and
            status.get('document_count', 0) > 0
        )
        
        response = {
            'status': 'healthy' if overall_healthy else 'unhealthy',
            'timestamp': None,
            'components': status
        }
        
        return jsonify(response), 200 if overall_healthy else 503
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@system_bp.route('/status', methods=['GET'])
@rate_limit(requests_per_minute=30)
def system_status():
    """Detailed system status endpoint"""
    try:
        search_service = current_app.search_service
        status = search_service.get_system_status()
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"System status failed: {e}")
        return jsonify({'error': 'Failed to get system status'}), 500

@system_bp.route('/info', methods=['GET'])
def system_info():
    """System information endpoint"""
    try:
        info = {
            'name': 'Semantic Search Application',
            'version': '1.0.0',
            'description': 'Production-ready semantic search with multiple approaches',
            'features': [
                'Semantic Search (Dense Vector)',
                'Keyword Search (BM25-style)',
                'Hybrid Search (Combined)',
                'Real-time Performance Metrics',
                'Multiple Search Approaches'
            ],
            'technologies': [
                'Python Flask',
                'Qdrant Vector Database',
                'Sentence Transformers',
                'TailwindCSS',
                'Alpine.js'
            ],
            'endpoints': {
                'search': '/api/search',
                'health': '/api/health',
                'status': '/api/status',
                'sample_queries': '/api/sample-queries'
            }
        }
        
        return jsonify(info)
        
    except Exception as e:
        logger.error(f"System info failed: {e}")
        return jsonify({'error': 'Failed to get system info'}), 500

@system_bp.route('/metrics', methods=['GET'])
@rate_limit(requests_per_minute=10)
def system_metrics():
    """System performance metrics endpoint"""
    try:
        search_service = current_app.search_service
        
        # Basic metrics
        metrics = {
            'cache_size': len(search_service.embedding_cache),
            'document_count': len(search_service.sample_data),
            'model_loaded': bool(search_service.model),
            'qdrant_connected': bool(search_service.client)
        }
        
        # Add collection metrics if available
        if search_service.client:
            try:
                collection_info = search_service.client.get_collection(search_service.config.COLLECTION_NAME)
                metrics['collection_metrics'] = {
                    'vectors_count': collection_info.vectors_count,
                    'indexed_vectors_count': collection_info.indexed_vectors_count,
                    'status': collection_info.status
                }
            except:
                metrics['collection_metrics'] = {'error': 'Collection not found'}
        
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"System metrics failed: {e}")
        return jsonify({'error': 'Failed to get system metrics'}), 500