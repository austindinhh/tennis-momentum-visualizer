"""Sidebar components for tournament and player selection."""

import datetime
from typing import Any

import streamlit as st


def render_sidebar() -> dict[str, Any] | None:
    """Render the sidebar with match selection options."""
    with st.sidebar:
        st.header("Match Selection")

        # Tournament selection
        tournament_options = {
            "Australian Open": "ausopen",
            "French Open": "frenchopen",
            "Wimbledon": "wimbledon",
            "US Open": "usopen",
        }

        tournament_name = st.selectbox(
            "Tournament",
            options=list(tournament_options.keys()),
            index=2,  # Default to Wimbledon
            help="Select the Grand Slam tournament",
        )
        tournament_url = tournament_options[tournament_name]

        # Year selection
        year = st.selectbox(
            "Year",
            options=list(range(2024, 2010, -1)),
            index=5,  # Default to 2019
            help="Tournament year (2011-2024)",
        )

        # Player inputs
        st.subheader("Players")

        # Player name suggestions/examples
        with st.expander("Player Name Examples", expanded=False):
            st.markdown("""
            **Men's Players:**
            - Novak Djokovic
            - Roger Federer
            - Rafael Nadal
            - Andy Murray
            - Stan Wawrinka

            **Women's Players:**
            - Serena Williams
            - Simona Halep
            - Angelique Kerber
            - Victoria Azarenka
            - Caroline Wozniacki
            """)

        player1 = st.text_input("Player 1", value="Novak Djokovic", help="Enter full first and last name")

        player2 = st.text_input("Player 2", value="Roger Federer", help="Enter full first and last name")

        # Quick match suggestions
        st.subheader("Famous Matches")
        famous_matches = {
            "Djokovic vs Federer (Wimbledon 2019)": {
                "tournament": "Wimbledon",
                "year": 2019,
                "player1": "Novak Djokovic",
                "player2": "Roger Federer",
            },
            "Nadal vs Federer (Australian Open 2017)": {
                "tournament": "Australian Open",
                "year": 2017,
                "player1": "Rafael Nadal",
                "player2": "Roger Federer",
            },
            "Murray vs Djokovic (US Open 2012)": {
                "tournament": "US Open",
                "year": 2012,
                "player1": "Andy Murray",
                "player2": "Novak Djokovic",
            },
        }

        selected_match = st.selectbox(
            "Or select a famous match:",
            options=["Custom", *list(famous_matches.keys())],
            help="Pre-configured famous matches",
        )

        # Update fields if famous match selected
        if selected_match != "Custom":
            match_info = famous_matches[selected_match]
            tournament_name = match_info["tournament"]
            tournament_url = tournament_options[tournament_name]
            year = match_info["year"]
            player1 = match_info["player1"]
            player2 = match_info["player2"]

            # Update the selectbox values (note: this is for display, actual values come from above)
            st.info(f"Selected: {selected_match}")

        # Analysis options
        st.subheader("Analysis Options")

        animation_type = st.radio(
            "Visualization Style",
            options=["Time-based", "Point-based"],
            index=0,
            help="Time-based: momentum over match duration\nPoint-based: momentum over point sequence",
        )

        # Advanced options
        with st.expander("Advanced Options", expanded=False):
            show_key_moments = st.checkbox(
                "Highlight Key Moments", value=True, help="Mark significant momentum shifts on charts",
            )

            smooth_momentum = st.checkbox(
                "Smooth Momentum Data", value=False, help="Apply smoothing to reduce noise in momentum calculations",
            )

            chart_theme = st.selectbox(
                "Chart Theme", options=["Default", "Dark", "Minimal"], help="Choose chart appearance theme",
            )

        # Validation and analysis button
        st.markdown("---")

        # Input validation feedback
        validation_messages = []
        NAME_LENGTH = 2

        if not player1.strip():
            validation_messages.append("⚠️ Player 1 name is required")
        elif len(player1.strip().split()) < NAME_LENGTH:
            validation_messages.append("⚠️ Player 1 needs first and last name")

        if not player2.strip():
            validation_messages.append("⚠️ Player 2 name is required")
        elif len(player2.strip().split()) < NAME_LENGTH:
            validation_messages.append("⚠️ Player 2 needs first and last name")

        if validation_messages:
            for msg in validation_messages:
                st.warning(msg)

        # Analysis button
        analysis_ready = len(validation_messages) == 0

        if st.button("🔍 Analyze Match", type="primary", use_container_width=True, disabled=not analysis_ready):
            if analysis_ready:
                return {
                    "tournament_url": tournament_url,
                    "tournament_name": tournament_name,
                    "year": year,
                    "player1": player1.strip(),
                    "player2": player2.strip(),
                    "animation_type": animation_type,
                    "show_key_moments": show_key_moments,
                    "smooth_momentum": smooth_momentum,
                    "chart_theme": chart_theme,
                    "trigger_analysis": True,
                }

        # Additional information
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        **Data Source:** https://github.com/JeffSackmann/tennis_slam_pointbypoint
        **Coverage:** Grand Slams 2011-2024
        **Analysis:** Point-by-point momentum tracking
        """)

        # Data availability notice
        st.info("""
        💡 **Note:** Only matches with detailed point-by-point data are available.
        This typically includes high-profile matches and later tournament rounds.
        """)

    return None


def render_match_history_sidebar() -> None:
    """Render a sidebar section showing recent analyses."""
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []

    if st.session_state.analysis_history:
        st.subheader("📚 Recent Analyses")

        for i, analysis in enumerate(st.session_state.analysis_history[-5:]):  # Show last 5
            with st.expander(f"{analysis['player1']} vs {analysis['player2']} ({analysis['year']})", expanded=False):
                st.write(f"**Tournament:** {analysis['tournament']}")
                st.write(f"**Result:** {analysis.get('result', 'N/A')}")
                if st.button(f"Reload Analysis {i + 1}", key=f"reload_{i}"):
                    # Logic to reload previous analysis would go here
                    st.info("Reload functionality would be implemented here")


def add_to_analysis_history(tournament_name: str, year: int, player1: str, player2: str, result: str | None = None) -> None:
    """Add a completed analysis to the history."""
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []

    analysis_record = {
        "tournament": tournament_name,
        "year": year,
        "player1": player1,
        "player2": player2,
        "result": result,
        "timestamp": datetime.now(),
    }

    # Avoid duplicates
    existing = [
        a
        for a in st.session_state.analysis_history
        if a["tournament"] == tournament_name
        and a["year"] == year
        and a["player1"] == player1
        and a["player2"] == player2
    ]

    if not existing:
        st.session_state.analysis_history.append(analysis_record)

        # Keep only last 10 analyses
        if len(st.session_state.analysis_history) > 10:
            st.session_state.analysis_history = st.session_state.analysis_history[-10:]
