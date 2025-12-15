"""Main Streamlit application for the Offline RAG Knowledge Portal."""
import streamlit as st
import os
from pathlib import Path
from typing import Optional, Dict
import time

from utils.config_loader import ConfigLoader
from knowledge_manager import KnowledgeManager
from rag_engine import RAGEngine
from embedding_generator import EmbeddingGenerator
from vector_db import VectorDatabase
from database import Database
from incremental_learning import IncrementalLearning
from utils.memory_monitor import MemoryMonitor

# Page configuration
st.set_page_config(
    page_title="Offline RAG Knowledge Portal",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'config' not in st.session_state:
    st.session_state.config = None
if 'knowledge_manager' not in st.session_state:
    st.session_state.knowledge_manager = None
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None


@st.cache_resource
def load_config():
    """Load configuration (cached)."""
    return ConfigLoader()


@st.cache_resource
def initialize_components(_config):
    """Initialize knowledge management components (cached)."""
    # Initialize shared Vector DB instance
    vector_db = VectorDatabase(_config)
    
    # Inject into KnowledgeManager and RAGEngine
    knowledge_manager = KnowledgeManager(_config, vector_db=vector_db)
    embedding_gen = EmbeddingGenerator(_config)
    rag_engine = RAGEngine(_config, embedding_gen, vector_db)
    
    return knowledge_manager, rag_engine


def login_page():
    """Display login page."""
    st.title("🔐 Login to Knowledge Portal")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    config = load_config()
                    db = Database(config)
                    user = db.authenticate_user(username, password)
                    
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.config = config
                        knowledge_manager, rag_engine = initialize_components(config)
                        st.session_state.knowledge_manager = knowledge_manager
                        st.session_state.rag_engine = rag_engine
                        st.success("Login successful!")
                        time.sleep(0.5)
                        st.rerun()  # Streamlit 1.28+ uses st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        st.info("**Default credentials:** admin / admin123 (change after first login!)")


def main_page():
    """Main application page."""
    # Sidebar
    with st.sidebar:
        st.title("📚 Knowledge Portal")
        st.markdown("---")
        
        # User info
        if st.session_state.user:
            st.success(f"Logged in as: **{st.session_state.user['username']}**")
            st.caption(f"Role: {st.session_state.user['role']}")
        
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["🔍 Search", "📄 Documents", "📊 Statistics", "👥 User Management", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Memory status
        if st.session_state.config:
            memory_monitor = MemoryMonitor(
                max_memory_mb=st.session_state.config.get('memory.max_memory_usage_mb', 6000)
            )
            memory_status = memory_monitor.get_memory_status()
            st.caption(f"💾 {memory_status}")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    # Main content based on page selection
    if page == "🔍 Search":
        search_page()
    elif page == "📄 Documents":
        documents_page()
    elif page == "📊 Statistics":
        statistics_page()
    elif page == "👥 User Management":
        user_management_page()
    elif page == "⚙️ Settings":
        settings_page()


def search_page():
    """Search and query interface."""
    st.title("🔍 Search Knowledge Base")
    st.markdown("---")
    
    # Search bar
    query = st.text_input(
        "Enter your query:",
        placeholder="What would you like to know?",
        key="search_query"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        top_k = st.slider("Number of results", 1, 20, 5)
    with col2:
        search_button = st.button("🔍 Search", use_container_width=True)
    
    if search_button and query:
        if st.session_state.rag_engine:
            with st.spinner("Searching knowledge base..."):
                results = st.session_state.rag_engine.query(
                    query,
                    top_k=top_k,
                    user_role=st.session_state.user['role']
                )
            
            # Display AI response
            st.markdown("### 💡 AI Response")
            st.info(results['response'])
            
            # Log search
            if st.session_state.user:
                db = Database(st.session_state.config)
                db.log_search(
                    st.session_state.user['id'],
                    query,
                    results['result_count']
                )
            
            # Display search results
            st.markdown("---")
            st.markdown(f"### 📋 Found {results['result_count']} relevant results")
            
            for i, result in enumerate(results['results'], 1):
                with st.expander(f"Result {i}: {result.get('file_name', 'Unknown')} (Score: {result.get('score', 0):.3f})"):
                    st.markdown(f"**Source:** `{result.get('file_path', 'Unknown')}`")
                    st.markdown(f"**Relevance Score:** {result.get('score', 0):.3f}")
                    st.markdown("**Excerpt:**")
                    st.text(result.get('text', 'No text available'))
        else:
            st.error("RAG engine not initialized. Please restart the application.")


def documents_page():
    """Document management page."""
    st.title("📄 Document Management")
    st.markdown("---")
    
    user_role = st.session_state.user['role']
    
    # Check permissions
    if user_role not in ['admin', 'researcher']:
        st.warning("You don't have permission to manage documents.")
        return
    
    # Upload section
    st.markdown("### 📤 Upload Documents")
    uploaded_files = st.file_uploader(
        "Select documents to upload",
        type=['pdf', 'docx', 'pptx', 'txt', 'md', 'xlsx'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Upload and Process", type="primary"):
            if st.session_state.knowledge_manager:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    # Save uploaded file temporarily
                    temp_path = Path("./temp") / uploaded_file.name
                    temp_path.parent.mkdir(exist_ok=True)
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Process document
                    result = st.session_state.knowledge_manager.add_document(
                        str(temp_path),
                        st.session_state.user['username']
                    )
                    results.append(result)
                    
                    # Clean up temp file
                    temp_path.unlink()
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                status_text.empty()
                progress_bar.empty()
                
                # Display results
                st.markdown("### Upload Results")
                for result in results:
                    if result['status'] == 'success':
                        st.success(f"✅ {result['message']} ({result.get('chunks', 0)} chunks)")
                    elif result['status'] == 'exists':
                        st.info(f"ℹ️ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
                
                st.rerun()
    
    st.markdown("---")
    
    # Document list
    st.markdown("### 📚 Document Library")
    
    if st.session_state.knowledge_manager:
        db = Database(st.session_state.config)
        documents = db.get_all_documents(user_role)
        
        if documents:
            # Search/filter
            search_term = st.text_input("🔍 Filter documents", key="doc_filter")
            filtered_docs = [
                doc for doc in documents
                if search_term.lower() in doc['file_name'].lower()
            ] if search_term else documents
            
            st.markdown(f"**Total documents:** {len(filtered_docs)}")
            
            # Display documents in a table
            for doc in filtered_docs:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{doc['file_name']}**")
                    st.caption(f"Uploaded: {doc['upload_date']} | Chunks: {doc.get('chunk_count', 0)}")
                
                with col2:
                    file_size_mb = doc.get('file_size', 0) / (1024 * 1024)
                    st.metric("Size", f"{file_size_mb:.2f} MB")
                
                with col3:
                    st.markdown(f"**Status:** {doc.get('status', 'unknown')}")
                
                with col4:
                    if user_role == 'admin':
                        if st.button("🗑️ Delete", key=f"delete_{doc['file_hash']}"):
                            if st.session_state.knowledge_manager.delete_document(doc['file_hash']):
                                st.success("Document deleted!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to delete document")
        else:
            st.info("No documents in the knowledge base. Upload some documents to get started!")


def statistics_page():
    """Display knowledge base statistics."""
    st.title("📊 Knowledge Base Statistics")
    st.markdown("---")
    
    if st.session_state.knowledge_manager:
        stats = st.session_state.knowledge_manager.get_statistics()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Documents", stats['total_documents'])
        
        with col2:
            st.metric("Total Vectors", stats['total_vectors'])
        
        with col3:
            st.metric("Total Chunks", stats['total_chunks'])
        
        with col4:
            memory_usage = stats['memory_usage']
            st.metric("System Memory Used", f"{memory_usage['system_used_percent']:.1f}%")
        
        st.markdown("---")
        
        # Memory details
        st.markdown("### 💾 Memory Usage")
        memory_usage = stats['memory_usage']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**System Total:** {memory_usage['system_total_gb']:.2f} GB")
            st.markdown(f"**System Available:** {memory_usage['system_available_gb']:.2f} GB")
        
        with col2:
            st.markdown(f"**Process Memory:** {memory_usage['process_memory_mb']:.1f} MB")
            st.markdown(f"**Process Memory %:** {memory_usage['process_memory_percent']:.1f}%")
        
        # Vector DB info
        st.markdown("---")
        st.markdown("### 🗄️ Vector Database")
        st.markdown(f"**Dimension:** {stats['vector_db_dimension']}")
        
        # Recent documents
        st.markdown("---")
        st.markdown("### 📄 Recent Documents")
        db = Database(st.session_state.config)
        recent_docs = db.get_all_documents()[:10]
        
        if recent_docs:
            for doc in recent_docs:
                st.markdown(f"- **{doc['file_name']}** ({doc.get('chunk_count', 0)} chunks) - {doc['upload_date']}")
        else:
            st.info("No documents yet.")


def user_management_page():
    """User management (admin only)."""
    st.title("👥 User Management")
    st.markdown("---")
    
    user_role = st.session_state.user['role']
    
    if user_role != 'admin':
        st.warning("Only administrators can manage users.")
        return
    
    # Create new user
    st.markdown("### ➕ Create New User")
    with st.form("create_user_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_username = st.text_input("Username")
        with col2:
            new_password = st.text_input("Password", type="password")
        with col3:
            new_role = st.selectbox("Role", ["admin", "researcher", "viewer"])
        
        create_user = st.form_submit_button("Create User", use_container_width=True)
        
        if create_user:
            if new_username and new_password:
                db = Database(st.session_state.config)
                if db.create_user(new_username, new_password, new_role):
                    st.success(f"User '{new_username}' created successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Username already exists!")
            else:
                st.error("Please fill in all fields")
    
    st.markdown("---")
    
    # List users
    st.markdown("### 👤 Existing Users")
    db = Database(st.session_state.config)
    # Note: In production, add a method to list all users
    st.info("User listing feature - to be extended in production")


def settings_page():
    """Application settings."""
    st.title("⚙️ Settings")
    st.markdown("---")
    
    if st.session_state.config:
        st.markdown("### Configuration")
        st.json(st.session_state.config.config)
        
        st.markdown("---")
        st.markdown("### System Information")
        st.info("""
        **Offline RAG Knowledge Portal**
        - Complete offline operation
        - Optimized for 8GB RAM
        - Privacy-focused architecture
        """)
    else:
        st.error("Configuration not loaded")


# Main app logic
def main():
    """Main application entry point."""
    if not st.session_state.authenticated:
        login_page()
    else:
        main_page()


if __name__ == "__main__":
    main()

