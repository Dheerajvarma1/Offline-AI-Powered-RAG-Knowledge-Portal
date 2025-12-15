# Project Structure

```
hol/
│
├── app.py                          # Main Streamlit application
├── config.yaml                     # Configuration file
├── requirements.txt                # Python dependencies
├── setup.py                        # Setup script
├── test_installation.py           # Installation test script
│
├── README.md                       # Main documentation
├── QUICKSTART.md                   # Quick start guide
├── PROJECT_STRUCTURE.md           # This file
│
├── document_processor.py          # Document processing pipeline
├── embedding_generator.py         # Embedding generation
├── vector_db.py                   # FAISS vector database
├── rag_engine.py                  # RAG query engine
├── knowledge_manager.py           # Main orchestrator
├── database.py                    # SQLite database operations
├── incremental_learning.py        # Incremental learning system
│
├── utils/
│   ├── __init__.py
│   ├── config_loader.py           # Configuration loader
│   └── memory_monitor.py          # Memory monitoring
│
├── .streamlit/
│   └── config.toml                # Streamlit configuration
│
├── data/                          # Data directory (created on setup)
│   ├── documents/                 # Uploaded documents
│   ├── vector_index/              # FAISS index files
│   └── knowledge_portal.db        # SQLite database
│
├── logs/                          # Log files (created on setup)
└── temp/                          # Temporary files (created on setup)
```

## Core Components

### Application Layer
- **app.py**: Streamlit web interface with authentication, search, document management
- **setup.py**: Initialization script for first-time setup
- **test_installation.py**: Verify installation and dependencies

### Processing Layer
- **document_processor.py**: Extract text from PDF, DOCX, PPTX, TXT, MD, XLSX
- **embedding_generator.py**: Generate embeddings using sentence-transformers
- **vector_db.py**: FAISS-based vector database for similarity search
- **rag_engine.py**: RAG query processing with optional LLM integration

### Management Layer
- **knowledge_manager.py**: Orchestrates document ingestion and indexing
- **database.py**: SQLite database for metadata, users, and documents
- **incremental_learning.py**: Handles incremental updates to knowledge base

### Utilities
- **utils/config_loader.py**: YAML configuration management
- **utils/memory_monitor.py**: Memory usage tracking and optimization

## Data Flow

1. **Document Upload** → `document_processor.py` → Text extraction & chunking
2. **Chunking** → `embedding_generator.py` → Vector embeddings
3. **Embeddings** → `vector_db.py` → FAISS index storage
4. **Metadata** → `database.py` → SQLite storage
5. **Query** → `rag_engine.py` → Search & response generation
6. **Results** → `app.py` → Display to user

## Configuration

All settings are in `config.yaml`:
- Embedding model selection
- Document processing parameters
- Vector database settings
- Memory limits
- User roles and permissions
- LLM provider settings

## Memory Optimization

Optimizations for 8GB RAM:
- Lightweight embedding model (all-MiniLM-L6-v2, 80MB)
- Batch processing with memory checks
- Lazy loading of models
- Efficient chunking strategies
- Real-time memory monitoring
- Garbage collection triggers

## Security Features

- Password hashing (SHA256)
- Role-based access control
- Document-level permissions (extensible)
- Session management
- Local-only processing (no external APIs)

## Extensibility

The system is designed to be extended:
- Add new document formats in `document_processor.py`
- Integrate different LLM providers in `rag_engine.py`
- Customize roles and permissions in `database.py`
- Add new search strategies in `rag_engine.py`



