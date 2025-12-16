"""
Custom CSS styles for the Knowledge Portal.
Provides a clean, professional, and aesthetic look.
"""

def get_css() -> str:
    """Return the custom CSS string."""
    return """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        /* Global Styles */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: #1a1a1a;
        }

        /* Clean Background */
        .stApp {
            background-color: #f8f9fa;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e0e0e0;
        }

        [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] h1 {
            font-weight: 600;
            font-size: 1.5rem;
            color: #111827;
            padding-bottom: 20px;
        }

        /* Buttons (Professional Look) */
        div.stButton > button {
            background-color: #111827;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }

        div.stButton > button:hover {
            background-color: #374151;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border-color: #374151;
        }
        
        div.stButton > button:active {
            transform: translateY(1px);
        }

        /* Primary Button (Upload, etc.) */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
            border: none;
        }

        /* Input Fields */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #d1d5db;
            padding: 0.5rem;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
        }

        /* Cards / Expanders */
        .streamlit-expanderHeader {
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            font-weight: 500;
        }
        
        div[data-testid="stExpander"] {
            border: none;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            border-radius: 8px;
            background-color: white;
            margin-bottom: 1rem;
        }

        /* Success/Info Messages */
        .stAlert {
            border-radius: 8px;
            border: none;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }

        /* Login Card Centering */
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }

        /* Headers */
        h1, h2, h3 {
            color: #111827;
            font-weight: 600;
            letter-spacing: -0.025em;
        }
        
        h1 { font-size: 2.25rem !important; }
        h2 { font-size: 1.8rem !important; }
        h3 { font-size: 1.5rem !important; }

        /* Remove default streamlit menu/footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """
