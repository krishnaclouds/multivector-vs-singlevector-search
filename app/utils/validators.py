"""
Input Validation Utilities
"""

import re
from typing import Dict, Any, Optional

def validate_search_params(data: Dict[str, Any]) -> Optional[str]:
    """Validate search parameters"""
    
    # Check if query is provided
    if 'query' not in data:
        return "Query parameter is required"
    
    query = data.get('query', '').strip()
    
    # Check query length
    if not query:
        return "Query cannot be empty"
    
    if len(query) < 2:
        return "Query must be at least 2 characters long"
    
    if len(query) > 1000:
        return "Query cannot exceed 1000 characters"
    
    # Check for potentially harmful content
    if re.search(r'[<>{}"\']', query):
        return "Query contains invalid characters"
    
    # Validate max_results
    max_results = data.get('max_results', 10)
    if not isinstance(max_results, int) or max_results < 1 or max_results > 50:
        return "max_results must be an integer between 1 and 50"
    
    # Validate search_type
    search_type = data.get('search_type', 'all')
    valid_types = ['all', 'semantic', 'keyword', 'hybrid']
    if search_type not in valid_types:
        return f"search_type must be one of: {', '.join(valid_types)}"
    
    return None

def sanitize_query(query: str) -> str:
    """Sanitize search query"""
    # Remove potentially harmful characters
    query = re.sub(r'[<>{}"\']', '', query)
    
    # Normalize whitespace
    query = re.sub(r'\s+', ' ', query.strip())
    
    return query

def validate_document_id(doc_id: str) -> bool:
    """Validate document ID format"""
    # Simple alphanumeric with underscores validation
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', doc_id))

def validate_json_payload(data: Dict[str, Any], required_fields: list) -> Optional[str]:
    """Validate JSON payload has required fields"""
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"
    
    return None