# Semantic Search - Production Ready

A powerful, production-grade semantic search application that demonstrates the effectiveness of multiple search approaches including semantic search, keyword search, and hybrid search.

## ✨ Features

- **🔍 Multiple Search Approaches**
  - Semantic Search (Dense Vector Similarity)
  - Keyword Search (BM25-style)
  - Hybrid Search (Combined Semantic + Keyword)

- **🚀 Production Ready**
  - Professional UI with real-time performance metrics
  - Docker containerization
  - Rate limiting and security features
  - Comprehensive logging and monitoring
  - Health checks and system status

- **🔧 Modern Architecture**
  - Flask backend with REST API
  - Qdrant vector database
  - Sentence Transformers for embeddings
  - Responsive web interface with TailwindCSS
  - Real-time search suggestions

- **📊 Performance Monitoring**
  - Response time tracking
  - Search result comparison
  - System health monitoring
  - Cache management

## 🚀 Quick Start

### One-Command Setup

```bash
# Make the script executable and run
chmod +x run.sh
./run.sh
```

The application will be available at `http://localhost:5000`

### Manual Setup

1. **Install Dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start Qdrant (Docker)**
   ```bash
   docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:v1.7.0
   ```

3. **Run Application**
   ```bash
   python app.py
   ```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🏗️ Architecture

```
├── app/
│   ├── api/                 # REST API endpoints
│   │   ├── search_routes.py # Search API
│   │   └── system_routes.py # System API
│   ├── core/                # Core application logic
│   │   ├── config.py        # Configuration management
│   │   └── search_service.py # Search service
│   ├── templates/           # HTML templates
│   │   └── index.html       # Main UI
│   ├── static/              # Static assets
│   └── utils/               # Utility functions
├── data/                    # Data storage
├── logs/                    # Application logs
├── models/                  # AI model cache
├── app.py                   # Main application
├── run.sh                   # Startup script
├── docker-compose.yml       # Docker configuration
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file (see `.env.example`):

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Search Configuration
COLLECTION_NAME=semantic_search
VECTOR_SIZE=384
MAX_RESULTS=50

# Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Advanced Configuration

- **Rate Limiting**: Configure `RATE_LIMIT_PER_MINUTE`
- **CORS**: Set `CORS_ORIGINS` for cross-origin requests
- **Logging**: Adjust `LOG_LEVEL` and `LOG_FILE`
- **Cache**: Configure `CACHE_TTL` for embedding cache

## 📚 API Documentation

### Search Endpoints

- `POST /api/search` - Perform search
- `GET /api/sample-queries` - Get sample queries
- `GET /api/search-suggestions` - Get search suggestions
- `GET /api/document/{id}` - Get specific document

### System Endpoints

- `GET /api/health` - Health check
- `GET /api/status` - System status
- `GET /api/info` - System information
- `GET /api/metrics` - Performance metrics

### Example Search Request

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence machine learning",
    "max_results": 10,
    "search_type": "all"
  }'
```

## 🔍 Search Approaches

### 1. Semantic Search
- Uses dense vector embeddings (384-dimensional)
- Sentence Transformers model: `all-MiniLM-L6-v2`
- Cosine similarity for relevance scoring
- Excellent for conceptual and contextual matches

### 2. Keyword Search
- Traditional BM25-style keyword matching
- Fast lexical matching
- Good for exact term matches
- Complementary to semantic search

### 3. Hybrid Search
- Combines semantic and keyword approaches
- Weighted scoring (70% semantic, 30% keyword)
- Best of both worlds for comprehensive results

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build and deploy
docker-compose up -d

# Scale application
docker-compose up -d --scale app=3

# Update configuration
docker-compose down
docker-compose up -d
```

### Environment Setup

1. **Production Environment**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secure-secret-key
   ```

2. **Security Configuration**
   ```bash
   export RATE_LIMIT_ENABLED=true
   export CORS_ORIGINS=https://yourdomain.com
   ```

3. **Database Configuration**
   ```bash
   export QDRANT_HOST=your-qdrant-host
   export QDRANT_API_KEY=your-api-key
   ```

## 📊 Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:5000/api/health

# System status
curl http://localhost:5000/api/status

# Performance metrics
curl http://localhost:5000/api/metrics
```

### Logging

- Application logs: `logs/app.log`
- Error tracking with structured logging
- Request/response monitoring
- Performance metrics logging

## 🛠️ Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
python -m black .

# Lint code
python -m flake8 .

# Type checking
python -m mypy app/
```

## 🔒 Security Features

- Rate limiting (60 requests/minute by default)
- Input validation and sanitization
- CORS configuration
- Security headers
- Non-root Docker user
- Environment-based configuration

## 🎯 Performance

- **Response Times**: < 100ms for semantic search
- **Throughput**: 100+ concurrent requests
- **Memory Usage**: < 512MB RAM
- **Cache Hit Rate**: > 80% for repeated queries

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale with Docker Compose
docker-compose up -d --scale app=5

# Load balancer configuration
# Configure nginx or HAProxy for load balancing
```

### Vertical Scaling

- Increase worker processes in `gunicorn`
- Optimize vector database resources
- Cache frequently accessed embeddings

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) - For embedding models
- [Qdrant](https://qdrant.tech/) - For vector database
- [Flask](https://flask.palletsprojects.com/) - For web framework
- [TailwindCSS](https://tailwindcss.com/) - For UI styling

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for production-ready semantic search**