#!/bin/bash

# ASMuvera - Vespa Setup Script
# This script sets up and starts a local Vespa instance using Docker

set -e

echo "🚀 Starting Vespa setup..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop existing Vespa container if running
if docker ps -q --filter "name=vespa" | grep -q .; then
    echo "🛑 Stopping existing Vespa container..."
    docker stop vespa
    docker rm vespa
fi

# Create data directory for Vespa
mkdir -p $HOME/vespa-data

# Start Vespa container
echo "🐳 Starting Vespa container..."
docker run -d \
    --name vespa \
    --hostname vespa-container \
    --publish 8080:8080 \
    --publish 19071:19071 \
    --volume $HOME/vespa-data:/opt/vespa/var \
    vespaengine/vespa:latest

# Wait for Vespa to be ready
echo "⏳ Waiting for Vespa to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:19071/ApplicationStatus > /dev/null 2>&1; then
        echo "✅ Vespa is ready!"
        break
    fi
    
    echo "⏳ Waiting for Vespa... (attempt $((attempt + 1))/$max_attempts)"
    sleep 5
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Vespa failed to start within expected time"
    exit 1
fi

# Deploy the application
echo "📦 Deploying ASMuvera application..."
cd "$(dirname "$0")/../.."

# Create application package
mkdir -p vespa-app
cp -r vespa/* vespa-app/

# Deploy to Vespa
curl -X POST \
    --header "Content-Type: application/zip" \
    --data-binary @<(cd vespa-app && zip -r - .) \
    http://localhost:19071/application/v2/tenant/default/session

# Activate the application
curl -X PUT \
    http://localhost:19071/application/v2/tenant/default/session/2/prepared

echo "🎉 Vespa setup complete!"
echo ""
echo "📊 Vespa endpoints:"
echo "   - Application status: http://localhost:19071/ApplicationStatus"
echo "   - Search API: http://localhost:8080/search/"
echo "   - Document API: http://localhost:8080/document/v1/"
echo ""
echo "🔧 Next steps:"
echo "   1. Install Python dependencies: pip install -r requirements.txt"
echo "   2. Download data: python scripts/data_prep/download_msmarco.py"
echo "   3. Run indexing: python scripts/experiments/run_indexing.py"