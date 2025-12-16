"""Main Streamlit application for the Offline RAG Knowledge Portal."""
import streamlit as st
import os
from pathlib import Path
from typing import Optional, Dict
import time

from utils.config_loader import ConfigLoader
from utils.styles import get_css, get_login_css
from knowledge_manager import KnowledgeManager
from rag_engine import RAGEngine
from embedding_generator import EmbeddingGenerator
from vector_db import VectorDatabase
from database import Database
from incremental_learning import IncrementalLearning
from utils.memory_monitor import MemoryMonitor

# Page configuration
st.set_page_config(
    page_title="Knowledge Portal",
    page_icon=None,
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
    st.markdown(get_login_css(), unsafe_allow_html=True)
    
    # Inject logo if exists
    if Path("assets/logo.png").exists():
        from utils.styles import get_image_base64
        logo_b64 = get_image_base64("assets/logo.png")
        if logo_b64:
             st.markdown(f'<div class="logo-container"><img src="{logo_b64}" class="logo-img"></div>', unsafe_allow_html=True)

    # Centered layout using columns
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.title("Login")
        st.markdown("Welcome back. Please enter your credentials.")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
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
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        



def main_page():
    """Main application page."""
    st.markdown(get_css(), unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("Knowledge Portal")
        
        # User info
        if st.session_state.user:
            st.markdown(f"**{st.session_state.user['username']}**")
            st.caption(f"{st.session_state.user['role'].title()}")
        
        st.markdown("---")
        
        # Navigation
        user_role = st.session_state.user.get('role')
        
        if user_role == 'viewer':
            nav_options = ["Search", "Statistics"]
        else:
            nav_options = ["Search", "Documents", "Statistics"]
            
        if user_role == 'admin':
            nav_options.append("User Management")
            
        page = st.radio(
            "Navigation",
            nav_options,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Memory status
        if st.session_state.config:
            memory_monitor = MemoryMonitor(
                max_memory_mb=st.session_state.config.get('memory.max_memory_usage_mb', 6000)
            )
            memory_status = memory_monitor.get_memory_status()
            st.caption(f"System Status: {memory_status}")
        
        # Logout
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    # Main content based on page selection
    if page == "Search":
        search_page()
    elif page == "Documents":
        documents_page()
    elif page == "Statistics":
        statistics_page()
    elif page == "User Management":
        user_management_page()


def search_page():
    """Search and query interface."""
    st.title("Search Knowledge Base")
    st.markdown("Find answers from your documents instantly.")
    
    # Search bar
    query = st.text_input(
        "Search Query",
        placeholder="Type your question here...",
        key="search_query",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    search_button = st.button("Search", use_container_width=True, type="primary")
    top_k = 1
    
    if search_button and query:
        if st.session_state.rag_engine:
            with st.spinner("Processing..."):
                results = st.session_state.rag_engine.query(
                    query,
                    top_k=top_k,
                    user_role=st.session_state.user['role'],
                    user_department=st.session_state.user.get('department')
                )
            
            # Display AI response
            st.markdown("### AI Analysis")
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
            if st.session_state.user['role'] != 'viewer':
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"### Sources ({results['result_count']})")
                
                for i, result in enumerate(results['results'], 1):
                    with st.expander(f"{result.get('file_name', 'Unknown')}", expanded=True):
                        st.markdown(f"**Path:** `{result.get('file_path', 'Unknown')}`")
                        st.markdown(f"**Relevance:** {result.get('score', 0):.2f}")
                        st.markdown("---")
                        st.write(result.get('text', 'No text available'))
        else:
            st.error("System initializing. Please refresh.")


def documents_page():
    """Document management page."""
    st.title("Documents")
    st.markdown("Manage your knowledge base files.")
    
    user_role = st.session_state.user['role']
    
    # Check permissions
    if user_role not in ['admin', 'researcher']:
        st.warning("Access restricted to administrators.")
        return
    
    # Upload section
    with st.expander("Upload New Files", expanded=True):
        uploaded_files = st.file_uploader(
            "Select documents",
            type=['pdf', 'docx', 'pptx', 'txt', 'md', 'xlsx'],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            if st.button("Process Files", type="primary"):
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
                            st.session_state.user['username'],
                            department=st.session_state.user.get('department')
                        )
                        results.append(result)
                        
                        # Clean up temp file
                        temp_path.unlink()
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    # Display results
                    st.markdown("### Upload Status")
                    for result in results:
                        if result['status'] == 'success':
                            st.success(f"Added: {result['message']}")
                        elif result['status'] == 'exists':
                            st.info(f"Skipped: {result['message']}")
                        else:
                            st.error(f"Failed: {result['message']}")
                    
                    time.sleep(2)
                    st.rerun()
    
    st.markdown("---")
    
    # Document list
    st.markdown("### Library")
    
    if st.session_state.knowledge_manager:
        db = Database(st.session_state.config)
        documents = db.get_all_documents(
            user_role=user_role,
            user_department=st.session_state.user.get('department')
        )
        
        if documents:
            # Search/filter
            search_term = st.text_input("Filter files", key="doc_filter", label_visibility="collapsed", placeholder="Filter by name...")
            filtered_docs = [
                doc for doc in documents
                if search_term.lower() in doc['file_name'].lower()
            ] if search_term else documents
            
            st.caption(f"{len(filtered_docs)} documents found")
            
            # Display documents in a clean list
            for doc in filtered_docs:
                with st.expander(f"{doc['file_name']}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{doc['file_name']}**")
                        dept_display = doc.get('department') or 'Global/Admin'
                        st.caption(f"Dept: **{dept_display}** | Uploaded: {doc['upload_date']}")
                        st.write(f"Size: {doc.get('file_size', 0) / (1024 * 1024):.2f} MB")
                    with col2:
                        st.caption("Actions")
                        if user_role == 'admin':
                            if st.button("Delete File", key=f"delete_{doc['file_hash']}"):
                                if st.session_state.knowledge_manager.delete_document(doc['file_hash']):
                                    st.success("Deleted")
                                    time.sleep(0.5)
                                    st.rerun()
        else:
            st.info("Library is empty.")


def statistics_page():
    """Display knowledge base statistics."""
    st.title("System Statistics")
    
    if st.session_state.knowledge_manager:
        stats = st.session_state.knowledge_manager.get_statistics()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Documents", stats['total_documents'])
        with col2:
            st.metric("Vectors", stats['total_vectors'])
        with col3:
            st.metric("Chunks", stats['total_chunks'])
        with col4:
            st.metric("Memory", f"{stats['memory_usage']['system_used_percent']:.1f}%")
        
        st.markdown("---")
        
        # Detailed stats view
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Memory Details")
            st.write(f"System Available: {stats['memory_usage']['system_available_gb']:.2f} GB")
            st.write(f"Process Usage: {stats['memory_usage']['process_memory_mb']:.1f} MB")
        
        with col2:
            st.markdown("### Index Info")
            st.write(f"Dimensions: {stats['vector_db_dimension']}")
            st.write(f"Type: FAISS IndexIDMap")


def user_management_page():
    """User management (admin only)."""
    st.title("User Management")
    
    user_role = st.session_state.user['role']
    
    if user_role != 'admin':
        st.error("Unauthorized access.")
        return
    
    with st.form("create_user_form"):
        st.markdown("### Create New User")
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username")
            new_role = st.selectbox("Role", ["admin", "researcher", "viewer"])
            
            new_department = None
            if new_role != 'admin':
                new_department = st.text_input("Department")
                
        with col2:
            new_password = st.text_input("Password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            create_user = st.form_submit_button("Create User")
        
        if create_user:
            if new_username and new_password:
                if new_role != 'admin' and not new_department:
                     st.error("Department is required for non-admin users.")
                else:
                    db = Database(st.session_state.config)
                    if db.create_user(new_username, new_password, new_role, new_department):
                        st.success(f"User '{new_username}' created")
                    else:
                        st.error("Username already exists")


def settings_page():
    """Application settings."""
    st.title("Settings")
    
    if st.session_state.config:
        st.markdown("### Current Configuration")
        st.json(st.session_state.config.config)
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

