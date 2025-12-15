# Quick Start Guide

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note:** This will download:
- Sentence transformers model (~80MB) - automatically on first run
- PyTorch CPU version (~200MB)
- Other dependencies (~500MB total)

### 2. Run Setup Script

```bash
python setup.py
```

This will:
- Create necessary directories
- Initialize the database
- Create default admin user
- Test embedding model download

### 3. Start the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### 4. First Login

- **Username:** `admin`
- **Password:** `admin123`

**⚠️ IMPORTANT:** Change the password immediately after first login!

## Basic Usage

### Adding Documents

1. Click on **"📄 Documents"** in the sidebar
2. Click **"Upload Documents"**
3. Select your files (PDF, DOCX, TXT, etc.)
4. Click **"Upload and Process"**
5. Wait for processing to complete

### Searching

1. Go to **"🔍 Search"** page
2. Enter your query
3. Click **"🔍 Search"**
4. View AI-generated response and relevant document excerpts

### Managing Users (Admin Only)

1. Go to **"👥 User Management"**
2. Fill in username, password, and role
3. Click **"Create User"**

## Memory Optimization Tips

For systems with 8GB RAM:

1. **Process documents in small batches** (5-10 at a time)
2. **Close other applications** when processing large documents
3. **Monitor memory usage** in the Statistics page
4. **Use smaller chunk sizes** in `config.yaml` if needed

## Troubleshooting

### Out of Memory Errors

- Reduce `batch_size` in `config.yaml` (embedding section)
- Process fewer documents at once
- Close other applications
- Restart the application

### Model Download Issues

- Ensure you have internet connection for first-time model download
- After download, the model is cached locally
- Check `~/.cache/huggingface/` for cached models

### Slow Performance

- Reduce `chunk_size` in `config.yaml`
- Use smaller batch sizes
- Enable GPU if available (change `device: "cuda"` in config)

### Port Already in Use

If port 8501 is busy:
```bash
streamlit run app.py --server.port 8502
```

## Configuration

Edit `config.yaml` to customize:
- Embedding model
- Chunk size
- Memory limits
- User roles and permissions

## Next Steps

1. **Add your documents** to build the knowledge base
2. **Create user accounts** for your team
3. **Customize roles** and permissions
4. **Set up incremental learning** for continuous updates

## Support

For issues or questions:
- Check the README.md for detailed documentation
- Review config.yaml for all available options
- Check logs in `./logs/app.log`



