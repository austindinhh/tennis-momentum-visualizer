"""Visualization functions for tennis match momentum analysis."""

from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.utils import load_config


class MomentumVisualizer:
    """Handles all visualization tasks for tennis match analysis."""

    def __init__(self, config_path: str | None = None) -> None:
        self.config = load_config(config_path)
        self.colors = self.config.get("visualization", {}).get(
            "default_colors", {"player1": "#1f77b4", "player2": "#d62728"},
        )
        self.chart_config = self.config.get("visualization", {}).get(
            "chart", {"height": 500, "line_width": 3, "marker_size": 4},
        )


    def create_momentum_chart(self, match_data: dict[str, Any]) -> go.Figure:
        """Create the main momentum visualization chart."""
        df = match_data["df"]
        stats = match_data["stats"]

        fig = go.Figure()

        # Add momentum lines
        fig.add_trace(
            go.Scatter(
                x=df["x_axis"],
                y=df["P1Momentum"],
                mode="lines+markers",
                name=f"{stats['player1_name']} Momentum",
                line={"color": self.colors["player1"], "width": self.chart_config["line_width"]},
                marker={"size": self.chart_config["marker_size"]},
                hovertemplate=f"<b>{stats['player1_name']}</b><br>"
                 f"{stats['x_label']}: %{{x}}<br>"
                 "Momentum: %{y:.2f}<extra></extra>",
            ),
        )

        fig.add_trace(
            go.Scatter(
                x=df["x_axis"],
                y=df["P2Momentum"],
                mode="lines+markers",
                name=f"{stats['player2_name']} Momentum",
                line={"color": self.colors["player2"], "width": self.chart_config["line_width"]},
                marker={"size": self.chart_config["marker_size"]},
                hovertemplate=f"<b>{stats['player2_name']}</b><br>"
                 f"{stats['x_label']}: %{{x}}<br>"
                 "Momentum: %{y:.2f}<extra></extra>",
            ),
        )

        # Update layout
        fig.update_layout(
            title=f"{stats.get('tournament_name', 'Tournament')} {stats.get('year', '')}: "
            f"{stats['player1_name']} vs {stats['player2_name']}",
            xaxis_title=stats["x_label"],
            yaxis_title="Momentum",
            xaxis={"nticks": 15, "tickangle": 45},
            hovermode="x unified",
            height=self.chart_config["height"],
            showlegend=True,
            legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 0.01},
            template="plotly_white",
        )

        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")

        return fig


    def create_set_breakdown_chart(self, match_data: dict[str, Any]) -> go.Figure:
        """Create a chart showing momentum by set."""
        df = match_data["df"]
        stats = match_data["stats"]

        if "SetNo" not in df.columns:
            return self._create_empty_chart("Set data not available")

        # Create subplots for each set
        sets = sorted(df["SetNo"].unique())
        fig = make_subplots(
            rows=len(sets),
            cols=1,
            subplot_titles=[f"Set {int(s)}" for s in sets],
            shared_xaxes=True,
            vertical_spacing=0.05,
        )

        for i, set_no in enumerate(sets, 1):
            set_df = df[df["SetNo"] == set_no].reset_index(drop=True)

            fig.add_trace(
                go.Scatter(
                    x=set_df["x_axis"],
                    y=set_df["P1Momentum"],
                    mode="lines",
                    name=stats["player1_name"] if i == 1 else None,
                    line={"color": self.colors["player1"]},
                    showlegend=i == 1,
                ),
                row=i,
                col=1,
            )

            fig.add_trace(
                go.Scatter(
                    x=set_df["x_axis"],
                    y=set_df["P2Momentum"],
                    mode="lines",
                    name=stats["player2_name"] if i == 1 else None,
                    line={"color": self.colors["player2"]},
                    showlegend=i == 1,
                ),
                row=i,
                col=1,
            )

        fig.update_layout(title="Momentum by Set", height=150 * len(sets), template="plotly_white")

        fig.update_xaxes(title_text=stats["x_label"], row=len(sets), col=1)
        fig.update_yaxes(title_text="Momentum")

        return fig


    def create_momentum_distribution_chart(self, match_data: dict[str, Any]) -> go.Figure:
        """Create histogram showing momentum distribution."""
        df = match_data["df"]
        stats = match_data["stats"]

        fig = go.Figure()

        # Add histograms for both players
        fig.add_trace(
            go.Histogram(
                x=df["P1Momentum"],
                name=stats["player1_name"],
                opacity=0.7,
                marker_color=self.colors["player1"],
                nbinsx=30,
            ),
        )

        fig.add_trace(
            go.Histogram(
                x=df["P2Momentum"],
                name=stats["player2_name"],
                opacity=0.7,
                marker_color=self.colors["player2"],
                nbinsx=30,
            ),
        )

        fig.update_layout(
            title="Momentum Distribution",
            xaxis_title="Momentum Value",
            yaxis_title="Frequency",
            barmode="overlay",
            template="plotly_white",
            height=400,
        )

        return fig


    def create_momentum_heatmap(self, match_data: dict[str, Any]) -> go.Figure:
        """Create a heatmap showing momentum throughout the match."""
        df = match_data["df"]
        stats = match_data["stats"]

        # Calculate momentum difference (P1 - P2)
        momentum_diff = df["P1Momentum"] - df["P2Momentum"]

        # Create bins for visualization
        n_bins = min(50, len(df) // 10)  # Adjust based on data size
        bin_size = len(df) // n_bins

        heatmap_data = []
        x_labels = []

        for i in range(0, len(df), bin_size):
            chunk = momentum_diff.iloc[i : i + bin_size]
            if len(chunk) > 0:
                heatmap_data.append(chunk.mean())
                x_labels.append(f"Points {i + 1}-{min(i + bin_size, len(df))}")

        fig = go.Figure(
            data=go.Heatmap(
                z=[heatmap_data],
                x=x_labels,
                y=["Momentum Advantage"],
                colorscale="RdBu_r",
                zmid=0,
                colorbar={
                    "title": "Momentum Difference",
                },
                hovertemplate="<b>%{x}</b><br>Advantage: %{z:.2f}<extra></extra>",
            ),
        )

        fig.update_layout(
            title=f"Momentum Advantage Throughout Match<br>"
            f"<span style='color:{self.colors['player1']}'>Blue = {stats['player1_name']}</span> | "
            f"<span style='color:{self.colors['player2']}'>Red = {stats['player2_name']}</span>",
            height=200,
            template="plotly_white",
        )

        return fig


    def create_key_moments_chart(self, match_data: dict[str, Any], key_moments: dict[str, Any]) -> go.Figure:
        """Create a chart highlighting key moments in the match."""
        match_data["df"]
        stats = match_data["stats"]

        fig = self.create_momentum_chart(match_data)

        # Add markers for momentum shifts
        if key_moments.get("momentum_shifts"):
            shift_points = key_moments["momentum_shifts"]

            fig.add_trace(
                go.Scatter(
                    x=[
                        point["time"] if stats["animation_type"] == "Time-based" else point["point_number"]
                        for point in shift_points
                    ],
                    y=[max(point["p1_momentum"], point["p2_momentum"]) for point in shift_points],
                    mode="markers",
                    name="Key Moments",
                    marker={"size": 12, "color": "yellow", "symbol": "star", "line": {"width": 2, "color": "orange"}},
                    hovertemplate="<b>Key Moment</b><br>Point: %{x}<br>Peak Momentum: %{y:.2f}<extra></extra>",
                ),
            )

        fig.update_layout(title=fig.layout.title.text + " - Key Moments Highlighted")

        return fig


    def create_summary_metrics_chart(self, match_data: dict[str, Any]) -> go.Figure:
        """Create a summary chart with key metrics."""
        stats = match_data["stats"]

        # Prepare data for radar chart
        categories = ["Avg Momentum", "Max Momentum", "Dominant Points %", "Sets Won", "Peak Performance"]

        # Normalize values for radar chart
        p1_values = [
            stats.get("p1_avg_momentum", 0) / 10,  # Normalize to 0-10 scale
            stats.get("p1_max_momentum", 0) / 20,  # Normalize to 0-10 scale
            stats.get("p1_dominance_pct", 0) / 10,  # Already percentage
            stats.get("p1_sets", 0) * 3,  # Multiply to make visible
            stats.get("p1_max_momentum", 0) / 30,  # Different normalization for variety
        ]

        p2_values = [
            stats.get("p2_avg_momentum", 0) / 10,
            stats.get("p2_max_momentum", 0) / 20,
            stats.get("p2_dominance_pct", 0) / 10,
            stats.get("p2_sets", 0) * 3,
            stats.get("p2_max_momentum", 0) / 30,
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=p1_values,
                theta=categories,
                fill="toself",
                name=stats["player1_name"],
                line_color=self.colors["player1"],
            ),
        )

        fig.add_trace(
            go.Scatterpolar(
                r=p2_values,
                theta=categories,
                fill="toself",
                name=stats["player2_name"],
                line_color=self.colors["player2"],
            ),
        )

        fig.update_layout(
            polar={"radialaxis": {"visible": True, "range": [0, 10]}},
            showlegend=True,
            title="Match Performance Summary",
            height=400,
        )

        return fig


    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create an empty chart with a message."""
        fig = go.Figure()
        fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font={"size": 16})
        fig.update_layout(xaxis={"visible": False}, yaxis={"visible": False}, height=300, template="plotly_white")

        return fig


    def export_chart(self, fig: go.Figure, filename: str, format: str = "html") -> bool:
        """Export chart to file."""
        try:
            if format.lower() == "html":
                fig.write_html(filename)
            elif format.lower() == "png" or format.lower() == "pdf":
                fig.write_image(filename)
            else:
                return False
            return True
        except Exception as e:
            print(f"Error exporting chart: {e}")
            return False
