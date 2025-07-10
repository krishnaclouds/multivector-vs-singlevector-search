#!/usr/bin/env python3
"""
Muvera Project Setup Script
Comprehensive setup and initialization for the Muvera research project
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
import yaml

def run_command(cmd, description="", check=True):
    """Run a shell command with error handling"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        return False

def check_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check if Docker is available for Vespa
    docker_available = run_command("docker --version", "Checking Docker", check=False)
    if not docker_available:
        print("⚠️  Docker not found - Vespa setup may require manual installation")
    
    return True

def setup_environment():
    """Setup Python virtual environment and dependencies"""
    print("\n📦 Setting up environment...")
    
    # Create virtual environment
    if not Path("venv").exists():
        run_command("python3 -m venv venv", "Creating virtual environment")
    
    # Install dependencies
    pip_cmd = "./venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip.exe"
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")
    
    # Install PyTorch with appropriate backend
    if sys.platform == "darwin":
        run_command(f"{pip_cmd} install torch torchvision torchaudio", "Installing PyTorch")
    elif sys.platform == "linux":
        # Check for CUDA
        cuda_available = run_command("nvidia-smi", "Checking CUDA", check=False)
        if cuda_available:
            run_command(f"{pip_cmd} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118", 
                       "Installing PyTorch with CUDA")
        else:
            run_command(f"{pip_cmd} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu", 
                       "Installing PyTorch (CPU)")
    
    return True

def setup_vespa():
    """Setup Vespa search platform"""
    print("\n🚀 Setting up Vespa...")
    
    # Create Vespa application
    vespa_dir = Path("vespa")
    if not vespa_dir.exists():
        print("❌ Vespa configuration directory not found")
        return False
    
    # Start Vespa using Docker
    vespa_cmd = """
    docker run --detach --name vespa --hostname vespa-container \
      --publish 8080:8080 --publish 19071:19071 \
      vespaengine/vespa:latest
    """
    
    if run_command("docker ps | grep vespa", "Checking if Vespa is running", check=False):
        print("✅ Vespa is already running")
    else:
        run_command(vespa_cmd, "Starting Vespa container")
        
        # Wait for Vespa to be ready
        import time
        print("⏳ Waiting for Vespa to be ready...")
        time.sleep(30)
        
        # Deploy application
        run_command("cd vespa && zip -r ../vespa-app.zip .", "Creating Vespa application package")
        run_command("curl -X POST --data-binary @vespa-app.zip http://localhost:19071/application/v2/tenant/default/prepareandactivate", 
                   "Deploying Vespa application")
    
    return True

def setup_data_directories():
    """Create necessary data directories"""
    print("\n📁 Setting up data directories...")
    
    directories = [
        "data/raw",
        "data/processed", 
        "data/embeddings",
        "evaluation/benchmarks",
        "evaluation/metrics",
        "evaluation/reports",
        "logs"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_path}")
    
    return True

def create_env_file():
    """Create environment configuration file"""
    print("\n⚙️ Creating environment configuration...")
    
    env_content = """# Muvera Environment Configuration
VESPA_ENDPOINT=http://localhost:8080
VESPA_DOCUMENT_API=http://localhost:8080/document/v1
VESPA_SEARCH_API=http://localhost:8080/search/

# Data settings
DATA_DIR=./data
MAX_PASSAGES=100000

# Model settings
SINGLE_VECTOR_MODEL=sentence-transformers/all-MiniLM-L6-v2
MULTI_VECTOR_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/muvera.log
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Environment file created: .env")
    return True

def validate_setup():
    """Validate the setup"""
    print("\n🔬 Validating setup...")
    
    # Check Python environment
    python_cmd = "./venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python.exe"
    if not run_command(f"{python_cmd} -c 'import torch; import sentence_transformers; print(\"Dependencies OK\")'", 
                      "Checking Python dependencies", check=False):
        print("❌ Python dependencies validation failed")
        return False
    
    # Check Vespa
    if not run_command("curl -s http://localhost:8080/ApplicationStatus", 
                      "Checking Vespa status", check=False):
        print("⚠️  Vespa validation failed - may need manual setup")
        return False
    
    print("✅ Setup validation complete")
    return True

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Muvera Project Setup")
    parser.add_argument("--skip-vespa", action="store_true", help="Skip Vespa setup")
    parser.add_argument("--skip-data", action="store_true", help="Skip data download")
    parser.add_argument("--dev", action="store_true", help="Development setup")
    
    args = parser.parse_args()
    
    print("🎯 Muvera Project Setup")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Setup data directories
    setup_data_directories()
    
    # Create environment file
    create_env_file()
    
    # Setup Vespa
    if not args.skip_vespa:
        setup_vespa()
    
    # Validate setup
    validate_setup()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("   1. Activate environment: source venv/bin/activate")
    print("   2. Download data: python scripts/data_prep/download_msmarco.py")
    print("   3. Generate embeddings: python scripts/data_prep/generate_embeddings.py")
    print("   4. Run experiments: python scripts/experiments/run_indexing.py")
    print("   5. Start UI: python src/ui/web_ui.py")
    
    if args.dev:
        print("\n🔧 Development setup:")
        print("   - Install development dependencies: pip install -e .")
        print("   - Run tests: python -m pytest tests/")
        print("   - Code formatting: black src/ tests/")
        print("   - Type checking: mypy src/")

if __name__ == "__main__":
    main()