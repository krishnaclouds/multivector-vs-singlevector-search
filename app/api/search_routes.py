"""
Search API Routes
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from app.utils.rate_limiter import rate_limit
from app.utils.validators import validate_search_params

logger = logging.getLogger(__name__)

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['POST'])
@rate_limit(requests_per_minute=60)
def search():
    """Main search endpoint"""
    try:
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Validate parameters
        validation_error = validate_search_params(data)
        if validation_error:
            return jsonify({'error': validation_error}), 400
        
        # Extract parameters
        query = data.get('query', '').strip()
        max_results = min(data.get('max_results', 10), 50)  # Limit to 50 results
        search_type = data.get('search_type', 'all')  # all, semantic, keyword, hybrid
        
        # Get search service
        search_service = current_app.search_service
        
        # Perform search based on type
        if search_type == 'semantic':
            results = {
                'query': query,
                'approaches': {
                    'semantic': search_service.search_semantic(query, max_results)
                }
            }
        elif search_type == 'keyword':
            results = {
                'query': query,
                'approaches': {
                    'keyword': search_service.search_keyword(query, max_results)
                }
            }
        elif search_type == 'hybrid':
            results = {
                'query': query,
                'approaches': {
                    'hybrid': search_service.search_hybrid(query, max_results)
                }
            }
        else:
            # Default: all approaches
            results = search_service.search_all_approaches(query, max_results)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return jsonify({'error': 'Search failed'}), 500

@search_bp.route('/sample-queries', methods=['GET'])
def sample_queries():
    """Get sample queries for testing"""
    queries = [
        "artificial intelligence machine learning",
        "climate change environmental impact",
        "space exploration mars mission",
        "quantum computing algorithms",
        "biotechnology genetic engineering",
        "renewable energy solar power",
        "cybersecurity data protection",
        "blockchain cryptocurrency technology",
        "medical research drug discovery",
        "robotics automation industry",
        "neural networks deep learning",
        "sustainable development goals",
        "satellite communication systems",
        "quantum entanglement physics",
        "CRISPR gene editing technology",
        "wind energy turbine design",
        "network security protocols",
        "digital currency economics",
        "cancer treatment research",
        "autonomous vehicle technology"
    ]
    
    return jsonify({'queries': queries})

@search_bp.route('/search-suggestions', methods=['GET'])
def search_suggestions():
    """Get search suggestions based on query prefix"""
    try:
        prefix = request.args.get('q', '').strip().lower()
        if not prefix or len(prefix) < 2:
            return jsonify({'suggestions': []})
        
        # Simple prefix matching on sample queries
        sample_queries = [
            "artificial intelligence", "machine learning", "deep learning",
            "climate change", "environmental science", "global warming",
            "space exploration", "mars mission", "astronomy",
            "quantum computing", "quantum physics", "quantum algorithms",
            "biotechnology", "genetic engineering", "CRISPR",
            "renewable energy", "solar power", "wind energy",
            "cybersecurity", "data protection", "network security",
            "blockchain", "cryptocurrency", "digital currency",
            "medical research", "drug discovery", "cancer treatment",
            "robotics", "automation", "autonomous vehicles"
        ]
        
        suggestions = [q for q in sample_queries if q.startswith(prefix)]
        suggestions = suggestions[:10]  # Limit to 10 suggestions
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        logger.error(f"Search suggestions failed: {e}")
        return jsonify({'suggestions': []})

@search_bp.route('/document/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get a specific document by ID"""
    try:
        search_service = current_app.search_service
        
        # Find document in sample data
        for doc in search_service.sample_data:
            if doc['id'] == doc_id:
                return jsonify(doc)
        
        return jsonify({'error': 'Document not found'}), 404
        
    except Exception as e:
        logger.error(f"Failed to get document {doc_id}: {e}")
        return jsonify({'error': 'Failed to retrieve document'}), 500