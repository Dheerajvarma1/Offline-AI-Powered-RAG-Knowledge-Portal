"""Setup script for initializing the knowledge portal."""
import os
import sys
from pathlib import Path

def setup():
    """Initialize the knowledge portal system."""
    print("=" * 60)
    print("Offline RAG Knowledge Portal - Setup")
    print("=" * 60)
    
    # Create necessary directories
    directories = [
        "./data",
        "./data/documents",
        "./data/vector_index",
        "./logs",
        "./temp"
    ]
    
    print("\n📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    # Check Python version
    print("\n🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("  ❌ Python 3.8+ required")
        sys.exit(1)
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check if config exists
    print("\n⚙️  Checking configuration...")
    if not Path("config.yaml").exists():
        print("  ❌ config.yaml not found!")
        sys.exit(1)
    print("  ✓ config.yaml found")
    
    # Initialize database
    print("\n💾 Initializing database...")
    try:
        from utils.config_loader import ConfigLoader
        from database import Database
        
        config = ConfigLoader()
        db = Database(config)
        print("  ✓ Database initialized")
        print("  ✓ Default admin user created (username: admin, password: admin123)")
    except Exception as e:
        print(f"  ❌ Error initializing database: {e}")
        sys.exit(1)
    
    # Test embedding model download
    print("\n🤖 Testing embedding model...")
    try:
        from embedding_generator import EmbeddingGenerator
        print("  ⏳ Downloading embedding model (this may take a few minutes on first run)...")
        embedding_gen = EmbeddingGenerator(config)
        print(f"  ✓ Embedding model loaded: {config.get('embedding.model_name')}")
        print(f"  ✓ Embedding dimension: {embedding_gen.get_dimension()}")
    except Exception as e:
        print(f"  ⚠️  Warning: Could not load embedding model: {e}")
        print("  This is normal on first run. The model will download when you start the app.")
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("  1. Review config.yaml and adjust settings if needed")
    print("  2. Run: streamlit run app.py")
    print("  3. Login with: admin / admin123")
    print("  4. Change the default password immediately!")
    print("\n💡 Tip: For best performance on 8GB RAM, keep batch sizes small.")
    print("=" * 60)


if __name__ == "__main__":
    setup()



