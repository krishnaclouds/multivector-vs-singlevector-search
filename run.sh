#!/bin/bash

# Semantic Search Application - Production Startup Script
# This script handles all aspects of running the semantic search application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Semantic Search"
PYTHON_VERSION="3.8"
VENV_PATH="venv"
QDRANT_VERSION="1.7.0"
FLASK_PORT=5000
QDRANT_PORT=6333

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  🚀 $PROJECT_NAME - Production Startup Script${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python_version() {
    print_status "Checking Python version..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python $PYTHON_VERSION or higher."
        exit 1
    fi
    
    PYTHON_VERSION_INSTALLED=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION_INSTALLED found"
}

# Setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "$VENV_PATH" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv $VENV_PATH
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source $VENV_PATH/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup Qdrant (Docker)
setup_qdrant() {
    print_status "Setting up Qdrant vector database..."
    
    # Check if Docker is installed
    if ! command_exists docker; then
        print_warning "Docker not found. Installing Qdrant locally..."
        
        # For systems without Docker, provide instructions
        print_status "Please install Docker to run Qdrant, or run Qdrant manually:"
        print_status "docker run -p 6333:6333 qdrant/qdrant:v$QDRANT_VERSION"
        print_warning "Continuing without Qdrant - app will use in-memory search"
        return
    fi
    
    # Check if Qdrant is already running
    if docker ps --format "table {{.Names}}" | grep -q "qdrant"; then
        print_success "Qdrant is already running"
        return
    fi
    
    # Start Qdrant
    print_status "Starting Qdrant vector database..."
    docker run -d \
        --name qdrant \
        -p $QDRANT_PORT:6333 \
        -p 6334:6334 \
        -v $(pwd)/qdrant_storage:/qdrant/storage \
        qdrant/qdrant:v$QDRANT_VERSION
    
    # Wait for Qdrant to be ready
    print_status "Waiting for Qdrant to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:$QDRANT_PORT/health > /dev/null; then
            print_success "Qdrant is ready"
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            print_warning "Qdrant may not be ready yet, but continuing..."
        fi
    done
}

# Initialize configuration
init_config() {
    print_status "Initializing configuration..."
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data/processed
    mkdir -p data/embeddings
    mkdir -p models
    
    # Set environment variables
    export FLASK_ENV=production
    export FLASK_DEBUG=false
    export FLASK_PORT=$FLASK_PORT
    export QDRANT_HOST=localhost
    export QDRANT_PORT=$QDRANT_PORT
    export SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}
    
    print_success "Configuration initialized"
}

# Start the application
start_application() {
    print_status "Starting the application..."
    
    # Check if port is available
    if lsof -i :$FLASK_PORT > /dev/null 2>&1; then
        print_error "Port $FLASK_PORT is already in use. Please stop the service using that port."
        exit 1
    fi
    
    print_success "Starting $PROJECT_NAME on port $FLASK_PORT..."
    print_success "Application will be available at: http://localhost:$FLASK_PORT"
    
    # Start with gunicorn in production mode
    if command_exists gunicorn; then
        print_status "Starting with Gunicorn (production server)..."
        gunicorn --bind 0.0.0.0:$FLASK_PORT --workers 4 --worker-class sync "main:create_app()"
    else
        print_status "Starting with Flask development server..."
        $PYTHON_CMD main.py
    fi
}

# Health check
health_check() {
    print_status "Running health check..."
    
    # Wait a moment for the server to start
    sleep 3
    
    # Check if the application is responding
    if curl -s http://localhost:$FLASK_PORT/api/health > /dev/null; then
        print_success "Application is healthy"
        return 0
    else
        print_error "Application health check failed"
        return 1
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    
    # Stop Qdrant if we started it
    if docker ps --format "table {{.Names}}" | grep -q "qdrant"; then
        print_status "Stopping Qdrant..."
        docker stop qdrant > /dev/null 2>&1
        docker rm qdrant > /dev/null 2>&1
        print_success "Qdrant stopped"
    fi
    
    # Deactivate virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
        print_success "Virtual environment deactivated"
    fi
}

# Handle script interruption
trap cleanup EXIT INT TERM

# Show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start      Start the application (default)"
    echo "  setup      Setup environment only"
    echo "  clean      Clean up Docker containers and temp files"
    echo "  health     Check application health"
    echo "  stop       Stop the application and cleanup"
    echo "  help       Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  FLASK_PORT     Port for the Flask application (default: 5000)"
    echo "  QDRANT_PORT    Port for Qdrant database (default: 6333)"
    echo "  FLASK_ENV      Flask environment (default: production)"
    echo ""
}

# Main execution
main() {
    print_header
    
    case "${1:-start}" in
        "start")
            check_python_version
            setup_venv
            install_dependencies
            init_config
            setup_qdrant
            start_application
            ;;
        "setup")
            check_python_version
            setup_venv
            install_dependencies
            init_config
            setup_qdrant
            print_success "Setup completed successfully"
            ;;
        "clean")
            cleanup
            # Remove additional files
            rm -rf __pycache__ .pytest_cache *.pyc
            rm -rf logs/*.log
            print_success "Cleanup completed"
            ;;
        "health")
            health_check
            ;;
        "stop")
            cleanup
            print_success "Application stopped"
            ;;
        "help")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"