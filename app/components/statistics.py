"""Statistics display components for match analysis."""

from typing import Any

import polars as pl
import streamlit as st

from src import DataProcessor
from src.utils import format_time


def render_statistics(match_data: dict[str, Any], key_moments: dict[str, Any] | None = None) -> None:
    """Render comprehensive match statistics."""
    st.subheader("Match Statistics")

    # Render basic match info
    render_basic_match_info(match_data)

    # Render momentum statistics
    render_momentum_statistics(match_data)

    # Render key moments summary
    if key_moments:
        render_key_moments_summary(match_data, key_moments)


def render_basic_match_info(match_data: dict[str, Any]) -> None:
    """Render basic match information."""
    stats = match_data["stats"]

    # Tournament and players
    st.markdown(f"**Tournament:** {stats.get('tournament_name', 'N/A')} {stats.get('year', '')}")
    st.markdown(f"**Players:** {stats['player1_name']} vs {stats['player2_name']}")

    if stats.get("winner"):
        st.markdown(f"**Winner:** {stats['winner']}")

    if stats.get("final_score"):
        st.markdown(f"**Final Score:** {stats['final_score']}")

    # Basic metrics in columns
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Points", f"{stats['total_points']:,}")
        st.metric(f"{stats['player1_name']} Sets Won", stats.get("p1_sets", 0))

    with col2:
        # Format match duration
        duration_str = format_time(stats.get("match_duration", 0))

        st.metric("Match Duration", duration_str)
        st.metric(f"{stats['player2_name']} Sets Won", stats.get("p2_sets", 0))


def render_momentum_statistics(match_data: dict[str, Any]) -> None:
    """Render momentum-specific statistics."""
    data_processor = DataProcessor()
    stats = match_data["stats"]
    df = match_data["df"]

    st.markdown("### Momentum Analysis")

    # Momentum averages
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**{stats['player1_name']}**")
        p1_avg = stats.get("p1_avg_momentum", 0)
        p1_max = stats.get("p1_max_momentum", 0)

        p1_dominance = stats.get("p1_dominance_pct", 0)
        st.metric(
            "Dominance", f"{p1_dominance:.1f}%", help="Percentage of points where this player had momentum advantage",
        )

        p1_dominant_points = stats.get("p1_dominant_points", 0)
        st.metric(" Dominant Points", p1_dominant_points, help="Points where this player had higher momentum")

        st.metric("Average Momentum", f"{p1_avg:.1f}")
        st.metric("Peak Momentum", f"{p1_max:.1f}")

        consistency_score = data_processor.calculate_momentum_consistency(df["P1Momentum"], df["P2Momentum"])
        st.metric("Consistency", f"{consistency_score:.1f}/10", help="Higher scores indicate more consistent momentum")

    with col2:
        st.markdown(f"**{stats['player2_name']}**")
        p2_avg = stats.get("p2_avg_momentum", 0)
        p2_max = stats.get("p2_max_momentum", 0)

        p2_dominance = stats.get("p2_dominance_pct", 0)
        st.metric(
            "Dominance", f"{p2_dominance:.1f}%", help="Percentage of points where this player had momentum advantage",
        )

        p2_dominant_points = stats.get("p2_dominant_points", 0)
        st.metric("Dominant Points", p2_dominant_points, help="Points where this player had higher momentum")

        st.metric("Average Momentum", f"{p2_avg:.1f}")
        st.metric("Peak Momentum", f"{p2_max:.1f}")

        consistency_score = data_processor.calculate_momentum_consistency(df["P2Momentum"], df["P1Momentum"])
        st.metric("Consistency", f"{consistency_score:.1f}/10", help="Higher scores indicate more consistent momentum")


def render_detailed_set_breakdown(set_breakdown: list, stats: dict[str, Any]) -> None:
    """Render detailed set-by-set breakdown."""
    st.markdown("#### Set-by-Set Breakdown")

    p1_last_name = stats["player1_name"].split(" ")[-1]
    p2_last_name = stats["player2_name"].split(" ")[-1]

    set_data = [
        {
            "Set": f"Set {set_info['set_number']}",
            "Score": f"{set_info.get('p1_games', 0)} - {set_info.get('p2_games', 0)}",
            "Points Played": set_info.get("points_played", 0),
            "Duration (min)": set_info.get("duration", 0) // 60,
            f"{p1_last_name} Avg Momentum": f"{set_info.get('p1_avg_momentum', 0):.1f}",
            f"{p2_last_name} Avg Momentum": f"{set_info.get('p2_avg_momentum', 0):.1f}",
        }
        for set_info in set_breakdown
    ]

    if set_data:
        df_sets = pl.DataFrame(set_data)
        st.dataframe(df_sets, use_container_width=True, hide_index=True)


def render_key_moments_summary(match_data: dict[str, Any], key_moments: dict[str, Any]) -> None:
    """Render summary of key moments."""
    stats = match_data["stats"]
    st.markdown("### Key Moments Summary")

    # Momentum shifts count
    shifts_count = len(key_moments.get("momentum_shifts", []))
    st.metric("Significant Momentum Shifts", shifts_count)

    # Momentum swings
    momentum_swings = stats.get("momentum_swings", 0)
    st.metric("Momentum Swings", momentum_swings, help="Number of significant momentum changes during the match")

    # Peak moments
    peak_moments = key_moments.get("peak_moments", [])
    if peak_moments:
        st.markdown("#### Peak Performance Moments")
        for moment in peak_moments[:3]:
            st.markdown(
                f"- **{moment['player']}** at point {moment['point_number']} (momentum: {moment['momentum']:.1f})",
            )

    # Most dramatic shifts
    shifts = key_moments.get("momentum_shifts", [])
    if shifts:
        st.markdown("#### Most Dramatic Shifts")
        top_shifts = sorted(shifts, key=lambda x: x.get("momentum_change", 0), reverse=True)[:3]
        for i, shift in enumerate(top_shifts, 1):
            st.markdown(
                f"{i}. Point {shift.get('point_number', 'N/A')} - Change: {shift.get('momentum_change', 0):.1f}",
            )


def render_comparison_metrics(match_data: dict[str, Any]) -> None:
    """Render head-to-head comparison metrics."""
    stats = match_data["stats"]

    st.markdown("### Head-to-Head Comparison")

    comparison_data = {
        "Metric": ["Average Momentum", "Peak Momentum", "Dominant Points %", "Sets Won", "Consistency Score"],
        stats["player1_name"]: [
            stats.get("p1_avg_momentum", 0),
            stats.get("p1_max_momentum", 0),
            stats.get("p1_dominance_pct", 0),
            stats.get("p1_sets", 0) * 20,
            max(0, 10 - match_data["df"]["P1Momentum"].std()) if "P1Momentum" in match_data["df"].columns else 0,
        ],
        stats["player2_name"]: [
            stats.get("p2_avg_momentum", 0),
            stats.get("p2_max_momentum", 0),
            stats.get("p2_dominance_pct", 0),
            stats.get("p2_sets", 0) * 20,
            max(0, 10 - match_data["df"]["P2Momentum"].std()) if "P2Momentum" in match_data["df"].columns else 0,
        ],
    }

    df_comparison = pl.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)


def render_export_data_section(match_data: dict[str, Any]) -> None:
    """Render data export section."""
    st.markdown("### Export Statistics")

    stats = match_data["stats"]

    summary_stats = {
        "Tournament": stats.get("tournament_name", "N/A"),
        "Year": stats.get("year", "N/A"),
        "Player 1": stats["player1_name"],
        "Player 2": stats["player2_name"],
        "Winner": stats.get("winner", "N/A"),
        "Final Score": stats.get("final_score", "N/A"),
        "Total Points": stats["total_points"],
        "Match Duration (seconds)": stats.get("match_duration", 0),
        "P1 Average Momentum": stats.get("p1_avg_momentum", 0),
        "P2 Average Momentum": stats.get("p2_avg_momentum", 0),
        "P1 Peak Momentum": stats.get("p1_max_momentum", 0),
        "P2 Peak Momentum": stats.get("p2_max_momentum", 0),
        "Momentum Swings": stats.get("momentum_swings", 0),
    }

    summary_df = pl.DataFrame([summary_stats])

    col1, col2 = st.columns(2)

    with col1:
        csv_data = summary_df.write_csv()
        st.download_button(
            label="📊 Download Summary Stats",
            data=csv_data,
            file_name=f"match_summary_{stats['player1_name'].replace(' ', '_')}_vs_{stats['player2_name'].replace(' ', '_')}.csv",
            mime="text/csv",
        )

    with col2:
        full_csv = match_data["df"].write_csv()
        st.download_button(
            label="Download Full Data",
            data=full_csv,
            file_name=f"full_match_data_{stats['player1_name'].replace(' ', '_')}_vs_{stats['player2_name'].replace(' ', '_')}.csv",
            mime="text/csv",
        )
