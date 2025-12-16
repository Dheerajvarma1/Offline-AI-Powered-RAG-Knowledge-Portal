"""
Custom CSS styles for the Knowledge Portal.
Provides a clean, professional, and aesthetic look.
"""
import base64
from pathlib import Path

def get_image_base64(path: str) -> str:
    """Read and encode image to base64."""
    try:
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/jpg;base64,{encoded}"
    except Exception:
        return ""

def get_login_css() -> str:
    """Return CSS specifically for the login page with background image and logo."""
    # Try to load the background image
    bg_path = Path("assets/login_bg.jpg")
    logo_path = Path("assets/logo.png")
    bg_image_css = ""
    logo_css = ""
    
    if bg_path.exists():
        img_b64 = get_image_base64(str(bg_path))
        if img_b64:
            bg_image_css = f"""
            .stApp {{
                background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url("{img_b64}");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            """
    
    if logo_path.exists():
        logo_b64 = get_image_base64(str(logo_path))
        if logo_b64:
            logo_css = f"""
            .logo-container {{
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 999;
                width: 150px;
            }}
            .logo-img {{
                width: 100%;
                height: auto;
            }}
            """
            
    return f"""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        /* Global Styles */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif !important;
        }}
        
        {bg_image_css}
        
        {logo_css}

        /* Login Container Styling Override */
        .stTextInput > div > div > input {{
            background-color: rgba(255, 255, 255, 0.9);
        }}
        
        /* White text for login on dark background */
        h1, h2, h3, p, .stMarkdown {{
            color: #ffffff !important;
        }}
        
        /* Hide sidebar on login page */
        [data-testid="stSidebar"] {{
            display: none;
        }}
        
        /* Adjust main container padding */
        .block-container {{
            padding-top: 5rem !important;
            padding-bottom: 0rem !important;
        }}

        /* Form container transparent/glassy */
        div[data-testid="stForm"] {{
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        /* Clean Background for inputs */
        .stTextInput label {{
            color: white !important;
        }}
        
        /* Buttons */
        div.stButton > button {{
            background-color: #4f46e5;
            color: white;
            border: none;
            width: 100%;
        }}
        
        /* Remove default streamlit menu/footer */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
    </style>
    """

def get_css() -> str:
    """Return the custom CSS string for main pages."""
    return """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        /* Global Styles */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: #1a1a1a;
        }

        /* Reset background for main app */
        .stApp {
            background-image: none !important;
            background-color: #f8f9fa !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e0e0e0;
        }
        
        /* ... Rest of the original CSS ... */

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
