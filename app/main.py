#!/usr/bin/env python3
"""Tennis Match Momentum Analyzer - Streamlit Main App."""

from pathlib import Path
import sys
import time

import streamlit as st

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from app.components.charts import render_additional_charts, render_main_chart
from app.components.sidebar import render_sidebar
from app.components.statistics import render_statistics
from app.styles.custom import apply_custom_styles
from src import DataProcessor, MomentumVisualizer, TennisMatchAnalyzer

# Page configuration
st.set_page_config(
    page_title="Tennis Match Momentum Analyzer",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize session state
def initialize_session_state() -> None:
    """Initialize session state variables."""
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = TennisMatchAnalyzer()
    if "data_processor" not in st.session_state:
        st.session_state.data_processor = DataProcessor()
    if "visualizer" not in st.session_state:
        st.session_state.visualizer = MomentumVisualizer()
    if "match_data" not in st.session_state:
        st.session_state.match_data = None
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "key_moments" not in st.session_state:
        st.session_state.key_moments = None


def run_analysis(tournament_url: str, tournament_name: str, year: int, player1: str, player2: str, animation_type: str) -> None:
    """Run the tennis match analysis."""
    # Progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        analyzer = st.session_state.analyzer
        data_processor = st.session_state.data_processor

        # Update analyzer properties
        analyzer.tournament_url = tournament_url
        analyzer.tournament_name = tournament_name
        analyzer.year = year
        analyzer.player1 = player1
        analyzer.player2 = player2

        # Step 1: Validate inputs
        status_text.info("✅ Validating inputs...")
        progress_bar.progress(10)

        valid, message = analyzer.validate_inputs(tournament_url, year, player1, player2)
        if not valid:
            st.error(f"❌ {message}")
            return

        # Step 2: Download data
        status_text.info("📥 Downloading tournament data...")
        progress_bar.progress(20)

        if not analyzer.download_tournament_data(tournament_url, year):
            st.error("❌ Failed to download tournament data")
            return

        # Step 3: Find match
        status_text.info("🔍 Searching for match...")
        progress_bar.progress(40)

        match_id = analyzer.find_match_id(player1, player2)
        if match_id is None:
            st.error("❌ No match found for the specified players")
            return

        # Step 4: Load match data
        status_text.info("📊 Loading match data...")
        progress_bar.progress(60)

        df = analyzer.create_match_dataframe(match_id)
        if df is None:
            st.error("❌ Failed to load match data")
            return

        # Step 5: Process data
        status_text.info("⚙️ Processing momentum data...")
        progress_bar.progress(80)

        # Process data
        match_data = data_processor.process_match_data(df, animation_type)
        match_data["stats"]["tournament_name"] = tournament_name
        match_data["stats"]["year"] = year

        # Identify key moments
        key_moments = data_processor.identify_key_moments(match_data["df"])

        # Store in session state
        st.session_state.match_data = match_data
        st.session_state.key_moments = key_moments
        st.session_state.analysis_complete = True

        progress_bar.progress(100)
        status_text.success("✅ Analysis complete!")

        # Clean up temporary files
        analyzer.cleanup_files()

        # Clear progress indicators after a brief delay
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()

        # Rerun to update the display
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error during analysis: {e!s}")
        progress_bar.empty()
        status_text.empty()


def display_welcome_info() -> None:
    """Display welcome information when no analysis is loaded."""
    st.markdown("""
    ## Introduction

    This application analyzes momentum shifts in professional tennis matches from Grand Slam tournaments.
    Momentum refers to the perceived flow or direction of a match, often characterized by a player's ability to win consecutive points or games.
    It's a combination of psychological and physical factors that influence a player's performance and can shift throughout a match.

    ### Features:
    - **Real-time momentum tracking** throughout matches
    - **Interactive visualizations** with time-based or point-based analysis
    - **Comprehensive statistics** including set breakdowns and key moments
    - **Historical data** from 2011-2024 across all Grand Slams

    ### How to Use:
    1. Select a tournament and year from the sidebar
    2. Enter the names of both players
    3. Choose your preferred visualization type
    4. Click "Analyze Match" to begin

    ### Supported Tournaments:
    - Australian Open
    - French Open
    - Wimbledon
    - US Open
    """)


def display_instructions() -> None:
    """Display usage instructions."""
    st.markdown("""
    ## Instructions

    ### Player Names:
    - Use full first and last names
    - Examples: "Novak Djokovic", "Roger Federer"
    - Names are matched flexibly but must be accurate

    ### Visualization Types:
    - **Time-based**: Shows momentum over match duration
    - **Point-based**: Shows momentum over point sequence

    ### Tips:
    - Try famous matches like Djokovic vs Federer Wimbledon 2019
    - Check spelling of player names carefully
    - Some early-round matches may not have data available
    """)


def main() -> None:
    """Run the app."""
    # Initialize session state
    initialize_session_state()

    # Apply custom styles
    apply_custom_styles()

    # Main header
    st.markdown('<h1 class="main-header">🎾 Tennis Match Momentum Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # Render sidebar and get user inputs
    analysis_params = render_sidebar()

    # Handle analysis trigger
    if analysis_params and analysis_params.get("trigger_analysis"):
        run_analysis(
            analysis_params["tournament_url"],
            analysis_params["tournament_name"],
            analysis_params["year"],
            analysis_params["player1"],
            analysis_params["player2"],
            analysis_params["animation_type"],
        )

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.session_state.analysis_complete and st.session_state.match_data is not None:
            # Render main chart
            render_main_chart(st.session_state.match_data, st.session_state.visualizer)

            # Render additional charts in tabs
            render_additional_charts(
                st.session_state.match_data,
                st.session_state.visualizer,
                st.session_state.key_moments,
            )
        else:
            display_welcome_info()

    with col2:
        if st.session_state.analysis_complete and st.session_state.match_data is not None:
            render_statistics(st.session_state.match_data, st.session_state.key_moments)
        else:
            display_instructions()


if __name__ == "__main__":
    main()
