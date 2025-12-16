# Offline AI-Powered RAG Knowledge Portal

## Executive Summary

The Offline AI-Powered RAG Knowledge Portal is a secure, privacy-centric knowledge management system designed for restricted environments. Utilizing Retrieval-Augmented Generation (RAG) technology, it enables organizations to ingest, index, and semantically search across proprietary document repositories without any data leaving the local infrastructure. The system is engineered for efficiency, operating effectively on hardware with limited resources (optimized for 8GB RAM).

## Key Features

### 1. Security and Access Control
*   **Offline Architecture**: The complete pipeline—from data ingestion to query processing—runs locally. No external APIs or cloud services are required, ensuring compliance with strict data security protocols.
*   **Departmental Isolation**: The system implements strict data segregation. Users are assigned to specific departments and can restrictedly access only documents belonging to their unit. Admin users maintain oversight across all departments.
*   **Role-Based Access Control (RBAC)**:
    *   **Administrator**: Full system authority, including user management, document oversight across all departments, and system configuration.
    *   **Researcher**: Department-restricted access with capabilities to search and view full document contents and metadata.
    *   **Viewer**: Restricted interface designed for information consumption only. Viewers can query the AI but cannot browse raw document lists or see source citations, ensuring information flows only through the synthesized AI response.

### 2. Information Retrieval
*   **Semantic Search**: Utilizes the `all-MiniLM-L6-v2` embedding model to understand the contextual meaning of queries rather than relying solely on keyword matching.
*   **Retrieval-Augmented Generation**: Combines the precision of vector search with the generative capabilities of Large Language Models (LLMs) to provide direct, context-aware answers.
*   **Interactive Conversational Interface**: A dynamic chat system that maintains conversation history, enabling users to ask follow-up questions and refine their queries contextually.
*   **Multi-Format Support**: Native support for processing PDF, Microsoft Word (DOCX), PowerPoint (PPTX), Plain Text (TXT), Markdown (MD), and Excel (XLSX) files.

### 3. User Interface and Experience
*   **Professional Dashboard**: A clean, distraction-free interface built with Streamlit.
*   **Custom Branding**: Configured with organization-specific login backgrounds and logos for a cohesive corporate identity.
*   **Adaptive Navigation**: The application interface dynamically adjusts based on the logged-in user's role, hiding unauthorized features to simplify the user workflow.

## Technical Architecture

The system follows a modular layered architecture:

1.  **Presentation Layer**: Streamlit-based web interface handling user interactions and visualization.
2.  **Application Logic**: Python-based backend managing authentication, state management, and orchestration.
3.  **RAG Engine**:
    *   **Vector Database**: FAISS (Facebook AI Similarity Search) for high-speed similarity retrieval.
    *   **Metadata Store**: SQLite for durable storage of document attributes, user credentials, and permission settings.
    *   **Embedding Generator**: Sentence Transformers for text-to-vector conversion.
    *   **Conversation Manager**: Context engine that retains chat history to inform LLM responses.

## System Requirements

To ensure optimal performance, the host machine should meet the following specifications:

*   **Operating System**: Windows, Linux, or macOS
*   **Memory (RAM)**: Minimum 8GB
*   **Storage**: 2GB available space for models and application files
*   **Runtime**: Python 3.8 or higher

## Installation and Setup

### 1. Repository Setup
Clone the project repository to your local machine or download the source code.

### 2. Environment Configuration
Install the required Python dependencies using the provided requirements file:

```bash
pip install -r requirements.txt
```

### 3. Model Initialization
On the first run, the system will automatically download the necessary embedding models (~80MB).

### 4. LLM Configuration (Optional)
For the generative AI component to function, an LLM backend is required. This project is configured to interface with **Ollama**.
1.  Install Ollama from the official website.
2.  Pull a compatible model (e.g., Llama 2):
    ```bash
    ollama pull llama2
    ```

### 5. Application Launch
Initialize the database and start the web server:

```bash
python setup.py
streamlit run app.py
```

## User Manual

### Administrator Workflow
*   **Login**: Access the portal using the default credentials (reset these after first login).
    *   Username: `admin`
    *   Password: `admin123`
*   **User Management**: Navigate to the "User Management" section to create accounts.
    *   Important: When creating non-admin users, you must specify a "Department". This tag controls which documents the user can see.
*   **Global Document Management**: Upload documents that should be accessible to specific departments. If no department is specified during upload by an Admin, the document is treated as "Global" but may be hidden from restricted users depending on strict isolation settings.

### Researcher Workflow
*   **Document Upload**: Researchers can upload documents. These are automatically tagged with their assigned department.
*   **Conversational Knowledge Retrieval**: Use the "Knowledge Chat" interface to query the database.
    *   **Follow-up Questions**: The system remembers the context of the conversion. You can ask follow-up questions like "Can you elaborate on the second point?" or "Summarize that".
    *   **Session Management**: Use the "Clear Chat Conversation" button in the sidebar to reset the context and start a new topic.

### Viewer Workflow
*   **Search-Only Access**: Viewers have a streamlined chat interface focused solely on getting answers.
*   **Contextual Q&A**: Viewers can engage in a back-and-forth dialogue with the knowledge base to drill down into specific topics.
*   **Privacy-First**: The "Documents" listing page is disabled. Source citations are integrated into the AI response logic but raw document navigation is restricted.

## Troubleshooting

### Access Denied / Missing Documents
If a user cannot see a document, verify the following:
1.  **Department Matching**: The user's department must exactly match the document's tagged department.
2.  **Role Restrictions**: Viewers are intentionally prevented from browsing the document list.

### Application Errors
*   **Login Page Scrolling**: Ensure the browser is at 100% zoom. The CSS is optimized to fit a standard 1080p viewport without scrolling.
*   **Connection Refused**: Ensure the Ollama service is running in the background if attempting to generate AI responses.

## License

This software is provided under the MIT License for internal and educational use.



