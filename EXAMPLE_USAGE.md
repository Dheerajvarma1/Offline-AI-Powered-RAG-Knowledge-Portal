# Example Usage

## Basic Workflow

### 1. Initial Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py

# Test installation
python test_installation.py
```

### 2. Start the Application

```bash
streamlit run app.py
```

### 3. Login

- Username: `admin`
- Password: `admin123`

### 4. Add Documents

1. Navigate to "📄 Documents" page
2. Upload PDF, DOCX, or other supported formats
3. Wait for processing (progress bar will show)
4. Documents are automatically indexed

### 5. Search

1. Go to "🔍 Search" page
2. Enter a query like "What is the procedure for X?"
3. View AI-generated response with source citations
4. Click on results to see full document excerpts

## Programmatic Usage

### Adding Documents Programmatically

```python
from utils.config_loader import ConfigLoader
from knowledge_manager import KnowledgeManager

# Load configuration
config = ConfigLoader()

# Initialize knowledge manager
km = KnowledgeManager(config)

# Add a document
result = km.add_document(
    file_path="./documents/manual.pdf",
    uploaded_by="admin"
)

print(result)
```

### Querying the Knowledge Base

```python
from utils.config_loader import ConfigLoader
from embedding_generator import EmbeddingGenerator
from vector_db import VectorDatabase
from rag_engine import RAGEngine

# Initialize components
config = ConfigLoader()
embedding_gen = EmbeddingGenerator(config)
vector_db = VectorDatabase(config)
rag_engine = RAGEngine(config, embedding_gen, vector_db)

# Query
results = rag_engine.query(
    "What are the safety procedures?",
    top_k=5,
    user_role="researcher"
)

print(results['response'])
for result in results['results']:
    print(f"- {result['file_name']}: {result['score']:.3f}")
```

### Managing Users

```python
from utils.config_loader import ConfigLoader
from database import Database

config = ConfigLoader()
db = Database(config)

# Create a new user
db.create_user(
    username="researcher1",
    password="secure_password",
    role="researcher"
)

# Authenticate
user = db.authenticate_user("researcher1", "secure_password")
print(user)
```

## Configuration Examples

### Using a Different Embedding Model

Edit `config.yaml`:

```yaml
embedding:
  model_name: "sentence-transformers/all-mpnet-base-v2"  # Larger, more accurate
  batch_size: 16  # Reduce batch size for larger models
```

### Enabling GPU (if available)

```yaml
embedding:
  device: "cuda"  # Use GPU instead of CPU
  batch_size: 64  # Can use larger batches with GPU
```

### Adjusting Chunk Size

```yaml
document:
  chunk_size: 1024  # Larger chunks (more context, more memory)
  chunk_overlap: 100  # More overlap for better context
```

### Using Ollama for LLM

```yaml
llm:
  provider: "ollama"
  model_name: "llama2:7b"  # Or mistral:7b, etc.
  ollama_base_url: "http://localhost:11434"
```

First, install Ollama and pull a model:
```bash
# Install Ollama from https://ollama.ai
ollama pull llama2:7b
```

## Memory Optimization Tips

### For 8GB RAM Systems

1. **Keep batch sizes small:**
   ```yaml
   embedding:
     batch_size: 16  # Instead of 32
   ```

2. **Use smaller chunks:**
   ```yaml
   document:
     chunk_size: 256  # Instead of 512
   ```

3. **Process documents in small batches:**
   - Upload 5-10 documents at a time
   - Wait for processing to complete before uploading more

4. **Monitor memory:**
   - Check Statistics page regularly
   - Close other applications when processing

## Troubleshooting Examples

### Issue: Out of Memory

**Solution:**
```python
# Reduce batch size in config.yaml
embedding:
  batch_size: 8  # Very small for tight memory
```

### Issue: Slow Processing

**Solution:**
```yaml
# Use smaller chunks
document:
  chunk_size: 256
  chunk_overlap: 25
```

### Issue: Model Not Found

**Solution:**
```bash
# The model downloads automatically on first use
# If it fails, download manually:
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

## Advanced Usage

### Incremental Updates

The system supports incremental learning:

```python
from incremental_learning import IncrementalLearning
from knowledge_manager import KnowledgeManager
from utils.config_loader import ConfigLoader

config = ConfigLoader()
km = KnowledgeManager(config)
il = IncrementalLearning(config, km)

# Process new documents with incremental updates
results = il.process_new_documents(
    file_paths=["./new_doc1.pdf", "./new_doc2.pdf"],
    uploaded_by="admin"
)
```

### Custom Document Processing

Extend `document_processor.py` to add new formats:

```python
def _extract_from_custom_format(self, file_path: str) -> str:
    # Your custom extraction logic
    pass
```

### Custom Roles and Permissions

Edit `config.yaml`:

```yaml
rbac:
  roles:
    - name: "custom_role"
      permissions: ["read", "search", "custom_permission"]
```

## Best Practices

1. **Regular Backups**: Backup `data/` directory regularly
2. **Monitor Memory**: Check Statistics page before large uploads
3. **Incremental Updates**: Use incremental learning for updates
4. **User Management**: Create role-specific users for security
5. **Document Organization**: Use descriptive file names
6. **Regular Maintenance**: Rebuild index if many deletions occur



