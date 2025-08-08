"""Chart rendering components for tennis match analysis."""

from typing import Any

import streamlit as st

from app.components.statistics import render_detailed_set_breakdown
from src.utils import format_time


def render_main_chart(match_data: dict[str, Any], visualizer) -> None:
    """Render the main momentum visualization chart."""
    st.subheader("Match Momentum Visualization")

    # Create and display the main momentum chart
    fig = visualizer.create_momentum_chart(match_data)
    st.plotly_chart(fig, use_container_width=True)


def render_additional_charts(match_data: dict[str, Any], visualizer, key_moments: dict[str, Any] | None = None) -> None:
    """Render additional charts in tabs."""
    # Create tabs for different chart types
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📈 Set Breakdown", "📊 Distribution", "🌡️ Momentum Heatmap", "⭐ Key Moments", "📋 Summary"],
    )

    with tab1:
        st.subheader("Set-by-Set Momentum")
        try:
            fig_sets = visualizer.create_set_breakdown_chart(match_data)
            st.plotly_chart(fig_sets, use_container_width=True)

            # Add set statistics
            if "set_breakdown" in match_data["stats"] and match_data["stats"]:
                render_detailed_set_breakdown(match_data["stats"]["set_breakdown"], match_data["stats"])
        except Exception as e:
            st.error(f"Unable to create set breakdown: {e!s}")
            st.info("Set data may not be available for this match")

    with tab2:
        st.subheader("Momentum Distribution")
        try:
            fig_dist = visualizer.create_momentum_distribution_chart(match_data)
            st.plotly_chart(fig_dist, use_container_width=True)

            # Add distribution statistics
            render_distribution_stats(match_data)
        except Exception as e:
            st.error(f"Unable to create distribution chart: {e!s}")

    with tab3:
        st.subheader("Momentum Heatmap")
        try:
            fig_heatmap = visualizer.create_momentum_heatmap(match_data)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            st.info("💡 Blue indicates advantage for Player 1, Red for Player 2")
        except Exception as e:
            st.error(f"Unable to create heatmap: {e!s}")

    with tab4:
        st.subheader("Key Moments Analysis")
        if key_moments and key_moments.get("momentum_shifts"):
            try:
                fig_key = visualizer.create_key_moments_chart(match_data, key_moments)
                st.plotly_chart(fig_key, use_container_width=True)

                # Display key moments table
                render_key_moments_table(key_moments)
            except Exception as e:
                st.error(f"Unable to create key moments chart: {e!s}")
        else:
            st.info("No significant momentum shifts detected in this match")

    with tab5:
        st.subheader("Performance Summary")
        try:
            fig_summary = visualizer.create_summary_metrics_chart(match_data)
            st.plotly_chart(fig_summary, use_container_width=True)

            # Add summary insights
            render_match_insights(match_data, key_moments)
        except Exception as e:
            st.error(f"Unable to create summary chart: {e!s}")


def render_distribution_stats(match_data: dict[str, Any]) -> None:
    """Render momentum distribution statistics."""
    stats = match_data["stats"]

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            f"{stats['player1_name']} Avg Momentum",
            f"{stats.get('p1_avg_momentum', 0):.2f}",
            help="Average momentum throughout the match",
        )
        st.metric(
            f"{stats['player1_name']} Peak",
            f"{stats.get('p1_max_momentum', 0):.2f}",
            help="Highest momentum point reached",
        )

    with col2:
        st.metric(
            f"{stats['player2_name']} Avg Momentum",
            f"{stats.get('p2_avg_momentum', 0):.2f}",
            help="Average momentum throughout the match",
        )
        st.metric(
            f"{stats['player2_name']} Peak",
            f"{stats.get('p2_max_momentum', 0):.2f}",
            help="Highest momentum point reached",
        )


def render_key_moments_table(key_moments: dict[str, Any]) -> None:
    """Render table of key moments."""
    if not key_moments.get("momentum_shifts"):
        return

    st.subheader("Significant Momentum Shifts")

    shifts = key_moments["momentum_shifts"][:10]  # Show top 10

    for i, moment in enumerate(shifts, 1):
        with st.expander(f"Key Moment #{i} - Point {moment.get('point_number', 'N/A')}", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Point Number:** {moment.get('point_number', 'N/A')}")
                st.write(f"**Elapsed Time:** {format_time(moment.get('time', 0))}")

            with col2:
                st.write(f"**Momentum Change:** {moment.get('momentum_change', 0):.2f}")
                st.write(f"**P1 Momentum:** {moment.get('p1_momentum', 0):.2f}")
                st.write(f"**P2 Momentum:** {moment.get('p2_momentum', 0):.2f}")


def render_match_insights(match_data: dict[str, Any], key_moments: dict[str, Any] | None = None) -> None:
    """Render match insights."""
    stats = match_data["stats"]
    df = match_data["df"]

    st.subheader("Match Insights")

    insights = []

    # Momentum dominance insight
    p1_dominance = stats.get("p1_dominance_pct", 0)
    p2_dominance = stats.get("p2_dominance_pct", 0)
    DOMINATED_PERCENTAGE_THRESHOLD = 60

    if p1_dominance > DOMINATED_PERCENTAGE_THRESHOLD:
        insights.append(f"**{stats['player1_name']}** dominated momentum for {p1_dominance:.1f}% of points")
    elif p2_dominance > DOMINATED_PERCENTAGE_THRESHOLD:
        insights.append(f"**{stats['player2_name']}** dominated momentum for {p2_dominance:.1f}% of points")
    else:
        insights.append("**Evenly matched** - momentum was closely contested throughout")

    # Match length insight
    total_points = stats.get("total_points", 0)
    LONG_MATCH_TOTAL_POINTS = 200
    SHORT_MATCH_TOTAL_POINTS = 100

    if total_points > LONG_MATCH_TOTAL_POINTS:
        insights.append(f"**Marathon match** - {total_points} points played")
    elif total_points < SHORT_MATCH_TOTAL_POINTS:
        insights.append(f"**Quick match** - only {total_points} points played")

    # Momentum swings insight
    HIGH_MOMENTUM_SHIFTS = 10
    LOW_MOMENTUM_SHIFTS = 3

    if key_moments and key_moments.get("momentum_shifts"):
        swing_count = len(key_moments["momentum_shifts"])
        if swing_count > HIGH_MOMENTUM_SHIFTS:
            insights.append(f"**High drama** - {swing_count} significant momentum shifts")
        elif swing_count < LOW_MOMENTUM_SHIFTS:
            insights.append("**Steady match** - few major momentum changes")

    # Peak performance insight
    p1_peak = stats.get("p1_max_momentum", 0)
    p2_peak = stats.get("p2_max_momentum", 0)

    if p1_peak > p2_peak * 1.5:
        insights.append(f"**{stats['player1_name']}** reached exceptional peak momentum ({p1_peak:.1f})")
    elif p2_peak > p1_peak * 1.5:
        insights.append(f"**{stats['player2_name']}** reached exceptional peak momentum ({p2_peak:.1f})")

    # Match pace analysis
    total_time = stats.get("match_duration", 0)
    total_points = stats.get("total_points", 1)  # Avoid division by zero
    SLOW_AVG_PT_DURATION = 30
    FAST_AVG_PT_DURATION = 15

    if total_time > 0:
        avg_point_duration = total_time / total_points # includes changeovers, medical timeouts, etc; not fully accurate
        if avg_point_duration > SLOW_AVG_PT_DURATION:
            insights.append("**Slow-paced match** - long rallies on average")
        elif avg_point_duration < FAST_AVG_PT_DURATION:
            insights.append("**Fast-paced match** - quick points")
        else:
            insights.append("**Moderate pace** - typical point duration")

    # Momentum volatility
    if "P1Momentum" in df.columns and "P2Momentum" in df.columns:
        momentum_diff = df["P1Momentum"] - df["P2Momentum"]
        volatility = momentum_diff.std()
        HIGH_VOLATILITY = 5
        LOW_VOLATILITY = 2

        if volatility > HIGH_VOLATILITY:
            insights.append("**High volatility** - momentum swung dramatically")
        elif volatility < LOW_VOLATILITY:
            insights.append("**Low volatility** - steady momentum throughout")
        else:
            insights.append("**Moderate volatility** - relatively balanced match")

    # Set length analysis
    if stats.get("set_breakdown"):
        set_lengths = [s.get("points_played", 0) for s in stats["set_breakdown"]]
        avg_set_length = sum(set_lengths) / len(set_lengths) if set_lengths else 0
        LONG_SET_LENGTH = 80
        SHORT_SET_LENGTH = 40

        if avg_set_length > LONG_SET_LENGTH:
            insights.append("**Long sets** - closely contested throughout")
        elif avg_set_length < SHORT_SET_LENGTH:
            insights.append("**Short sets** - dominated by one player")

    # Match competitiveness
    p1_dominance = stats.get("p1_dominance_pct", 0)
    p2_dominance = stats.get("p2_dominance_pct", 0)
    dominance_diff = abs(p1_dominance - p2_dominance)
    DOMINANCE_POINTS_THRESHOLD_HIGH = 30
    DOMINANCE_POINTS_THRESHOLD_LOW = 10

    if dominance_diff < DOMINANCE_POINTS_THRESHOLD_LOW:
        insights.append("**Highly competitive** - evenly matched players")
    elif dominance_diff > DOMINANCE_POINTS_THRESHOLD_HIGH:
        insights.append("**One-sided momentum** - one player felt in control the majority of the time")

    # Display insights
    for insight in insights:
        st.markdown(f"- {insight}")

    if not insights:
        st.info("Analysis complete - check individual charts for detailed insights")


def render_export_options(match_data: dict[str, Any], visualizer) -> None:
    """Render chart export options."""
    st.subheader("💾 Export Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Export Main Chart", help="Download momentum chart as HTML"):
            try:
                fig = visualizer.create_momentum_chart(match_data)
                stats = match_data["stats"]
                filename = f"{stats['player1_name']}_vs_{stats['player2_name']}_{stats['year']}.html"

                if visualizer.export_chart(fig, filename, "html"):
                    st.success(f"Chart exported as {filename}")
                else:
                    st.error("Export failed")
            except Exception as e:
                st.error(f"Export error: {e!s}")

    with col2:
        if st.button("📈 Export All Charts", help="Download complete analysis"):
            st.info("Full export functionality would be implemented here")

    with col3:
        if st.button("📋 Export Data", help="Download raw match data as CSV"):
            try:
                df = match_data["df"]
                csv = df.to_csv(index=False)
                st.download_button(label="Download CSV", data=csv, file_name="match_data.csv", mime="text/csv")
            except Exception as e:
                st.error(f"Data export error: {e!s}")
