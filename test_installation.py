"""Test script to verify installation and basic functionality."""
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import streamlit
        print("  ✓ streamlit")
    except ImportError as e:
        print(f"  ✗ streamlit: {e}")
        return False
    
    try:
        import sentence_transformers
        print("  ✓ sentence-transformers")
    except ImportError as e:
        print(f"  ✗ sentence-transformers: {e}")
        return False
    
    try:
        import faiss
        print("  ✓ faiss-cpu")
    except ImportError as e:
        print(f"  ✗ faiss-cpu: {e}")
        return False
    
    try:
        import yaml
        print("  ✓ pyyaml")
    except ImportError as e:
        print(f"  ✗ pyyaml: {e}")
        return False
    
    try:
        import psutil
        print("  ✓ psutil")
    except ImportError as e:
        print(f"  ✗ psutil: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()
        print("  ✓ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False

def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    
    try:
        from utils.config_loader import ConfigLoader
        from database import Database
        
        config = ConfigLoader()
        db = Database(config)
        print("  ✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False

def test_embedding_model():
    """Test embedding model (may download on first run)."""
    print("\nTesting embedding model...")
    print("  (This may take a few minutes on first run)")
    
    try:
        from utils.config_loader import ConfigLoader
        from embedding_generator import EmbeddingGenerator
        
        config = ConfigLoader()
        embedding_gen = EmbeddingGenerator(config)
        
        # Test with a simple sentence
        test_text = "This is a test sentence."
        embedding = embedding_gen.generate_embeddings(test_text)
        
        print(f"  ✓ Embedding model loaded")
        print(f"  ✓ Generated embedding with dimension: {embedding.shape}")
        return True
    except Exception as e:
        print(f"  ✗ Embedding model error: {e}")
        print("  (This is normal on first run - model will download when needed)")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Offline RAG Knowledge Portal - Installation Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Database", test_database()))
    results.append(("Embedding Model", test_embedding_model()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✅ All tests passed! You're ready to use the Knowledge Portal.")
        print("Run: streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("Make sure you've installed all dependencies: pip install -r requirements.txt")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())



