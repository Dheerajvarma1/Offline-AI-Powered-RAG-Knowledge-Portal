# Offline AI-Powered RAG Knowledge Portal

A completely offline, privacy-focused knowledge management system with Retrieval-Augmented Generation (RAG) capabilities, optimized for systems with 8GB RAM.

## Features

### Core Features
- **Complete Offline Operation**: No internet connection required
- **Local Hardware Optimization**: Efficient memory usage for 8GB RAM systems
- **Data Privacy Assurance**: All processing happens locally
- **Multi-format Document Support**: PDF, DOCX, PPTX, TXT, Markdown, Excel
- **Intelligent Search**: Semantic search with RAG-powered responses

### Bonus Features
- **Incremental Learning**: Add new documents without rebuilding entire index
- **Role-Based Access Control**: User authentication and document-level permissions
- **Memory Monitoring**: Real-time memory usage tracking
- **Batch Processing**: Efficient document ingestion

## System Requirements

- **RAM**: 8GB (optimized for this constraint)
- **Storage**: ~2GB for models and dependencies
- **OS**: Windows/Linux/macOS
- **Python**: 3.8+

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download lightweight embedding model** (automatically on first run):
   - Model: `sentence-transformers/all-MiniLM-L6-v2` (~80MB)
   - This is the most memory-efficient option

4. **Optional: Set up local LLM** (for generation):
   - Option A: Install Ollama and download a small model (e.g., `llama2:7b` or `mistral:7b`)
   - Option B: Use quantized models with llama-cpp-python
   - Option C: Use a simple template-based response system (included)

## Quick Start

1. **Initialize the system**:
```bash
python setup.py
```

2. **Start the web interface**:
```bash
streamlit run app.py
```

3. **Access the portal**:
   - Open browser to `http://localhost:8501`
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123` (change immediately!)

## Usage

### Adding Documents

1. Go to "Document Management" in the sidebar
2. Click "Upload Documents"
3. Select files (PDF, DOCX, TXT, etc.)
4. Documents are automatically processed and indexed

### Searching

1. Use the search bar on the main page
2. Enter your query
3. Get semantic search results with relevant document excerpts
4. View full documents and get AI-generated summaries

### User Management

1. Admin can create users with different roles:
   - **Admin**: Full access
   - **Researcher**: Can search and view all documents
   - **Viewer**: Limited document access based on permissions

## Architecture

```
┌─────────────────┐
│  Streamlit UI   │
└────────┬────────┘
         │
┌────────▼─────────────────────────┐
│      Application Layer           │
│  - Authentication & RBAC         │
│  - Query Processing              │
│  - Document Management           │
└────────┬─────────────────────────┘
         │
┌────────▼─────────────────────────┐
│      RAG Engine                  │
│  - Embedding Generation          │
│  - Vector Search (FAISS)         │
│  - Response Generation            │
└────────┬─────────────────────────┘
         │
┌────────▼─────────────────────────┐
│      Data Layer                  │
│  - Vector Database (FAISS)       │
│  - Metadata DB (SQLite)          │
│  - Document Storage               │
└──────────────────────────────────┘
```

## Memory Optimization

The system includes several optimizations for 8GB RAM:

1. **Lightweight Models**: Uses `all-MiniLM-L6-v2` (80MB) instead of larger models
2. **Efficient Chunking**: Smart document chunking to balance context and memory
3. **Lazy Loading**: Models loaded only when needed
4. **Batch Processing**: Documents processed in small batches
5. **Memory Monitoring**: Real-time tracking to prevent OOM errors
6. **FAISS Index**: Memory-efficient vector storage

## Configuration

Edit `config.yaml` to customize:
- Embedding model selection
- Chunk size and overlap
- Vector database settings
- User roles and permissions
- Memory limits

## Security & Privacy

- All data processed locally
- No external API calls
- Encrypted user credentials
- Document-level access control
- Audit logging

## Troubleshooting

### Out of Memory Errors
- Reduce batch size in `config.yaml`
- Process fewer documents at once
- Close other applications

### Slow Performance
- Use smaller embedding models
- Reduce chunk size
- Enable GPU if available (optional)

## License

MIT License - Use freely for internal knowledge management

## Contributing

This is a standalone system. Customize as needed for your organization's requirements.



