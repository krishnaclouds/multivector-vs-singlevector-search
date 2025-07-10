#!/usr/bin/env python3
"""
Muvera - Multi-Vector Search Research Platform
Main entry point for all project operations
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config import get_config

def setup_project():
    """Initialize the project"""
    print("🚀 Setting up Muvera project...")
    
    # Load configuration
    config = get_config()
    
    # Create necessary directories
    print("📁 Creating directories...")
    directories = [
        config.paths.data_dir,
        config.paths.raw_dir,
        config.paths.processed_dir,
        config.paths.embeddings_dir,
        config.paths.logs_dir
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_path}")
    
    print("✅ Project setup complete!")

def download_data():
    """Download and prepare data"""
    print("📥 Downloading data...")
    
    try:
        from scripts.data_prep.download_msmarco import main as download_main
        download_main()
    except ImportError:
        print("❌ Data download script not found")
        sys.exit(1)

def generate_embeddings():
    """Generate embeddings"""
    print("🔧 Generating embeddings...")
    
    try:
        from scripts.data_prep.generate_embeddings import main as embeddings_main
        embeddings_main()
    except ImportError:
        print("❌ Embeddings generation script not found")
        sys.exit(1)

def run_indexing():
    """Run indexing experiments"""
    print("📊 Running indexing experiments...")
    
    try:
        from scripts.experiments.run_indexing import main as indexing_main
        indexing_main()
    except ImportError:
        print("❌ Indexing script not found")
        sys.exit(1)

def run_evaluation():
    """Run evaluation"""
    print("📈 Running evaluation...")
    
    try:
        from scripts.experiments.run_evaluation import main as evaluation_main
        evaluation_main()
    except ImportError:
        print("❌ Evaluation script not found")
        sys.exit(1)

def start_ui():
    """Start web UI"""
    print("🌐 Starting web UI...")
    
    try:
        from ui.web_ui import main as ui_main
        ui_main()
    except ImportError:
        print("❌ Web UI script not found")
        sys.exit(1)

def run_demo():
    """Run interactive demo"""
    print("🎮 Running interactive demo...")
    
    try:
        from ui.demo import main as demo_main
        demo_main()
    except ImportError:
        print("❌ Demo script not found")
        sys.exit(1)

def show_status():
    """Show project status"""
    print("📊 Muvera Project Status")
    print("=" * 40)
    
    config = get_config()
    
    # Check data files
    data_files = [
        ("Raw data", Path(config.paths.raw_dir) / "collection.tsv"),
        ("Processed passages", Path(config.paths.processed_dir) / "passages.jsonl"),
        ("Single vector embeddings", Path(config.paths.embeddings_dir) / "single_vector_passages.npy"),
        ("Multi vector embeddings", Path(config.paths.embeddings_dir) / "multi_vector_passages.npy")
    ]
    
    print("\n📁 Data Status:")
    for name, file_path in data_files:
        status = "✅" if file_path.exists() else "❌"
        size = f"({file_path.stat().st_size // (1024*1024)} MB)" if file_path.exists() else ""
        print(f"   {status} {name} {size}")
    
    # Check Vespa status
    print("\n🔍 Vespa Status:")
    try:
        import requests
        response = requests.get(f"{config.vespa.endpoint}/ApplicationStatus", timeout=5)
        if response.status_code == 200:
            print("   ✅ Vespa is running")
        else:
            print("   ❌ Vespa is not responding")
    except Exception:
        print("   ❌ Vespa is not accessible")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Muvera - Multi-Vector Search Research Platform")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Initialize project')
    
    # Data commands
    data_parser = subparsers.add_parser('download', help='Download data')
    embeddings_parser = subparsers.add_parser('embeddings', help='Generate embeddings')
    
    # Experiment commands
    index_parser = subparsers.add_parser('index', help='Run indexing experiments')
    eval_parser = subparsers.add_parser('evaluate', help='Run evaluation')
    
    # UI commands
    ui_parser = subparsers.add_parser('ui', help='Start web UI')
    demo_parser = subparsers.add_parser('demo', help='Run interactive demo')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show project status')
    
    # Pipeline command - run everything
    pipeline_parser = subparsers.add_parser('pipeline', help='Run complete pipeline')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'setup':
        setup_project()
    elif args.command == 'download':
        download_data()
    elif args.command == 'embeddings':
        generate_embeddings()
    elif args.command == 'index':
        run_indexing()
    elif args.command == 'evaluate':
        run_evaluation()
    elif args.command == 'ui':
        start_ui()
    elif args.command == 'demo':
        run_demo()
    elif args.command == 'status':
        show_status()
    elif args.command == 'pipeline':
        print("🚀 Running complete Muvera pipeline...")
        setup_project()
        download_data()
        generate_embeddings()
        run_indexing()
        run_evaluation()
        print("✅ Complete pipeline finished!")

if __name__ == "__main__":
    main()