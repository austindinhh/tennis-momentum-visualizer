"""Custom CSS styles for the Tennis Match Momentum Analyzer
"""

import streamlit as st


def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    st.markdown(
        """
    <style>
        /* Main header styling */
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
            color: #1f77b4;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        /* Metric container styling */
        .metric-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            border-left: 4px solid #1f77b4;
        }

        /* Enhanced alert styling */
        .stAlert > div {
            padding: 1rem;
            border-radius: 0.5rem;
        }

        /* Success message styling */
        .stSuccess > div {
            background-color: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }

        /* Info message styling */
        .stInfo > div {
            background-color: #d1ecf1;
            border-color: #bee5eb;
            color: #0c5460;
        }

        /* Warning message styling */
        .stWarning > div {
            background-color: #fff3cd;
            border-color: #ffeaa7;
            color: #856404;
        }

        /* Error message styling */
        .stError > div {
            background-color: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: #f8f9fa;
        }

        /* Button styling */
        .stButton > button {
            background-color: #1f77b4;
            color: white;
            border-radius: 0.5rem;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            background-color: #1565c0;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        /* Primary button styling */
        .stButton > button[kind="primary"] {
            background: linear-gradient(45deg, #1f77b4, #2196f3);
            box-shadow: 0 2px 4px rgba(31, 119, 180, 0.3);
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(45deg, #1565c0, #1976d2);
        }

        /* Selectbox styling */
        .stSelectbox > div > div {
            border-radius: 0.5rem;
        }

        /* Text input styling */
        .stTextInput > div > div > input {
            border-radius: 0.5rem;
            border: 2px solid #e0e0e0;
            transition: border-color 0.3s ease;
        }

        .stTextInput > div > div > input:focus {
            border-color: #1f77b4;
            box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.2);
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: #f0f2f6;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #1f77b4;
            color: white;
        }

        /* Metric value styling */
        [data-testid="metric-container"] {
            background-color: white;
            border: 1px solid #e0e0e0;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Plotly chart container */
        .js-plotly-plot {
            border-radius: 0.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            border: 1px solid #e0e0e0;
        }

        /* Radio button styling */
        .stRadio > div {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #e0e0e0;
        }

        /* Checkbox styling */
        .stCheckbox > label {
            background-color: #f8f9fa;
            padding: 0.5rem;
            border-radius: 0.25rem;
            border: 1px solid #e0e0e0;
        }

        /* Progress bar styling */
        .stProgress > div > div > div {
            background: linear-gradient(45deg, #1f77b4, #2196f3);
        }

        /* Dataframe styling */
        .dataframe {
            border-radius: 0.5rem;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Responsive design adjustments */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem;
            }

            .stButton > button {
                width: 100%;
                margin-bottom: 0.5rem;
            }
        }

        /* Animation for loading states */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .loading {
            animation: pulse 2s infinite;
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }

        /* Tennis-themed accents */
        .tennis-accent {
            border-left: 4px solid #228B22;
            padding-left: 1rem;
        }

        .court-green {
            background-color: #228B22;
            color: white;
        }

        .tennis-ball {
            background: radial-gradient(circle, #FFFF00, #FFD700);
        }

        /* Status indicators */
        .status-success {
            color: #28a745;
            font-weight: bold;
        }

        .status-warning {
            color: #ffc107;
            font-weight: bold;
        }

        .status-error {
            color: #dc3545;
            font-weight: bold;
        }

        .status-info {
            color: #17a2b8;
            font-weight: bold;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def get_chart_theme(theme_name: str = "default") -> dict:
    """Get chart theme configuration"""
    themes = {
        "default": {
            "template": "plotly_white",
            "colorway": ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e"],
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
        },
        "dark": {
            "template": "plotly_dark",
            "colorway": ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e"],
            "paper_bgcolor": "#2f2f2f",
            "plot_bgcolor": "#2f2f2f",
        },
        "minimal": {
            "template": "simple_white",
            "colorway": ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"],
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
        },
    }

    return themes.get(theme_name, themes["default"])


def apply_loading_animation():
    """Apply loading animation CSS"""
    st.markdown(
        """
    <style>
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #1f77b4;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 2s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            text-align: center;
            color: #1f77b4;
            font-weight: bold;
            animation: pulse 2s infinite;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def display_loading_spinner(text: str = "Loading..."):
    """Display a loading spinner with text"""
    apply_loading_animation()

    st.markdown(
        f"""
    <div class="loading-spinner"></div>
    <div class="loading-text">{text}</div>
    """,
        unsafe_allow_html=True,
    )
