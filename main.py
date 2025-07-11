#!/usr/bin/env python3
"""
Semantic Search Application
Production-ready semantic search with multiple search approaches
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from app.api.search_routes import search_bp
from app.api.system_routes import system_bp
from app.core.config import Config
from app.core.search_service import SearchService
from app.utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS for API endpoints
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']))
    
    # Register blueprints
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(system_bp, url_prefix='/api')
    
    # Initialize search service
    search_service = SearchService()
    app.search_service = search_service
    
    @app.route('/')
    def index():
        """Main application page"""
        return render_template('index.html')
    
    @app.route('/favicon.ico')
    def favicon():
        """Serve favicon"""
        return send_from_directory(
            os.path.join(app.root_path, 'app/static'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )
    
    @app.errorhandler(404)
    def not_found(error):
        """404 error handler"""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 error handler"""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.before_request
    def before_request():
        """Log incoming requests"""
        logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Development server
    if app.config['DEBUG']:
        logger.info("🚀 Starting Semantic Search Application in DEBUG mode")
        logger.info("📍 Access the interface at: http://localhost:5000")
        logger.info("🔍 Experience advanced semantic search capabilities!")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        logger.info("🚀 Starting Semantic Search Application in PRODUCTION mode")
        app.run(host='0.0.0.0', port=5000)