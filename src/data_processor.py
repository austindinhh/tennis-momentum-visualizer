"""Data processing functions for tennis match analysis."""

from typing import Any

import pandas as pd
import polars as pl

from src.utils import calculate_match_score, load_config, parse_time_to_seconds


class DataProcessor:
    """Handles data processing and transformation for tennis matches."""

    def __init__(self, config_path: str | None = None) -> None:
        self.config = load_config(config_path)


    def process_match_data(self, df: pl.DataFrame, animation_type: str = "Time-based") -> dict[str, Any]:
        """Process the match data for visualization."""
        # Convert Polars DataFrame to Pandas for easier integration
        df_pandas = df.to_pandas()

        # Process elapsed time
        df_pandas["cumulative_seconds"] = df_pandas["ElapsedTime"].apply(parse_time_to_seconds)

        # Convert data types
        df_pandas["PointNumber"] = df_pandas["PointNumber"].astype(int)
        df_pandas["P1Momentum"] = pd.to_numeric(df_pandas["P1Momentum"], errors="coerce")
        df_pandas["P2Momentum"] = pd.to_numeric(df_pandas["P2Momentum"], errors="coerce")

        # Fill any NaN values with 0
        df_pandas["P1Momentum"] = df_pandas["P1Momentum"].fillna(0)
        df_pandas["P2Momentum"] = df_pandas["P2Momentum"].fillna(0)

        # Choose x-axis based on animation type
        if animation_type == "Time-based":
            df_pandas["x_axis"] = df_pandas["cumulative_seconds"]
            x_label = "Elapsed Time (seconds)"
        else:
            df_pandas["x_axis"] = df_pandas["PointNumber"]
            x_label = "Point Number"

        # Calculate match statistics
        match_stats = self._calculate_match_statistics(df, df_pandas, x_label, animation_type)

        return {"df": df_pandas, "stats": match_stats}


    def _calculate_match_statistics(
        self, df_polars: pl.DataFrame, df: pd.DataFrame, x_label: str, animation_type: str,
    ) -> dict[str, Any]:
        """Calculate comprehensive match statistics."""
        stats = {
            "total_points": len(df),
            "match_duration": df["cumulative_seconds"].max() if "cumulative_seconds" in df.columns else 0,
            "player1_name": df["player1"].iloc[0] if not df.empty else "Player 1",
            "player2_name": df["player2"].iloc[0] if not df.empty else "Player 2",
            "x_label": x_label,
            "animation_type": animation_type,
        }

        # Calculate final score using utility function
        try:
            final_score, winner, p1_sets, p2_sets = calculate_match_score(df_polars)

            stats.update({"final_score": final_score, "winner": winner, "p1_sets": p1_sets, "p2_sets": p2_sets})
        except Exception:
            # Fallback if score calculation fails
            stats.update({"final_score": "Score unavailable", "winner": "Unknown", "p1_sets": 0, "p2_sets": 0})

        # Add momentum statistics
        stats.update(self._calculate_momentum_stats(df))

        # Add set-by-set breakdown
        stats.update(self._calculate_set_breakdown(df))

        return stats


    def _calculate_momentum_stats(self, df: pd.DataFrame) -> dict[str, Any]:
        """Calculate momentum-related statistics."""
        momentum_stats = {}

        if "P1Momentum" in df.columns and "P2Momentum" in df.columns:
            # Basic momentum statistics
            momentum_stats.update(
                {
                    "p1_avg_momentum": df["P1Momentum"].mean(),
                    "p2_avg_momentum": df["P2Momentum"].mean(),
                    "p1_max_momentum": df["P1Momentum"].max(),
                    "p2_max_momentum": df["P2Momentum"].max(),
                    "p1_min_momentum": df["P1Momentum"].min(),
                    "p2_min_momentum": df["P2Momentum"].min(),
                },
            )

            # Momentum swings (times when momentum changed significantly)
            momentum_diff = df["P1Momentum"] - df["P2Momentum"]
            momentum_swings = abs(momentum_diff.diff()).fillna(0)
            momentum_stats["momentum_swings"] = (momentum_swings > momentum_swings.median()).sum()

            # Periods of dominance
            p1_dominant_points = (df["P1Momentum"] > df["P2Momentum"]).sum()
            p2_dominant_points = (df["P2Momentum"] > df["P1Momentum"]).sum()

            momentum_stats.update(
                {
                    "p1_dominant_points": p1_dominant_points,
                    "p2_dominant_points": p2_dominant_points,
                    "p1_dominance_pct": (p1_dominant_points / len(df)) * 100,
                    "p2_dominance_pct": (p2_dominant_points / len(df)) * 100,
                },
            )

        return momentum_stats


    def _calculate_set_breakdown(self, df: pd.DataFrame) -> dict[str, Any]:
        """Calculate set-by-set statistics."""
        set_stats = {}

        if "SetNo" in df.columns:
            try:
                set_breakdown = []

                for set_no in sorted(df["SetNo"].unique()):
                    set_df = df[df["SetNo"] == set_no]

                    set_info = {
                        "set_number": int(set_no),
                        "points_played": len(set_df),
                        "duration": set_df["cumulative_seconds"].max() - set_df["cumulative_seconds"].min()
                        if "cumulative_seconds" in set_df.columns
                        else 0,
                    }

                    # Get final games for this set
                    if "P1GamesWon" in set_df.columns and "P2GamesWon" in set_df.columns:
                        set_info.update(
                            {
                                "p1_games": int(set_df["P1GamesWon"].iloc[-1]),
                                "p2_games": int(set_df["P2GamesWon"].iloc[-1]),
                            },
                        )

                    # Momentum stats for this set
                    if "P1Momentum" in set_df.columns and "P2Momentum" in set_df.columns:
                        set_info.update(
                            {
                                "p1_avg_momentum": set_df["P1Momentum"].mean(),
                                "p2_avg_momentum": set_df["P2Momentum"].mean(),
                            },
                        )

                    set_breakdown.append(set_info)

                set_stats["set_breakdown"] = set_breakdown
                set_stats["total_sets"] = len(set_breakdown)

            except Exception:
                set_stats["set_breakdown"] = []
                set_stats["total_sets"] = 0

        return set_stats


    def smooth_momentum_data(self, df: pd.DataFrame, window_size: int | None = None) -> pd.DataFrame:
        """Apply smoothing to momentum data."""
        if window_size is None:
            window_size = self.config.get("visualization", {}).get("momentum", {}).get("window_size", 5)

        df_smooth = df.copy()

        if "P1Momentum" in df.columns and "P2Momentum" in df.columns:
            df_smooth["P1Momentum"] = (
                df["P1Momentum"].rolling(window=window_size, center=True).mean().fillna(df["P1Momentum"])
            )
            df_smooth["P2Momentum"] = (
                df["P2Momentum"].rolling(window=window_size, center=True).mean().fillna(df["P2Momentum"])
            )

        return df_smooth


    def calculate_momentum_derivatives(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate momentum change rates."""
        df_with_derivatives = df.copy()

        if "P1Momentum" in df.columns and "P2Momentum" in df.columns:
            df_with_derivatives["P1Momentum_change"] = df["P1Momentum"].diff().fillna(0)
            df_with_derivatives["P2Momentum_change"] = df["P2Momentum"].diff().fillna(0)

            # Calculate acceleration (second derivative)
            df_with_derivatives["P1Momentum_accel"] = df_with_derivatives["P1Momentum_change"].diff().fillna(0)
            df_with_derivatives["P2Momentum_accel"] = df_with_derivatives["P2Momentum_change"].diff().fillna(0)

        return df_with_derivatives


    def calculate_momentum_consistency(self, player: pd.Series, opponent: pd.Series, epsilon: float = 1e-6) -> float:
        """Calculate a consistency score for a player's momentum over a match. Scaled out of 10."""
        # Metric 1: % of time ahead of opponent
        ahead_ratio = (player > opponent).median()

        # Metric 2: % of time above own average
        avg = player.median()
        above_own_avg = (player > avg).median()

        # Metric 3: Stability (inverse of normalized standard deviation)
        std_dev = player.std()
        range_ = player.max() - player.min()
        stability = 1 - (std_dev / (range_ + epsilon))

        # Metric 4: Growth score (momentum build-up over time)
        n = len(player)
        early_avg = player.iloc[: n // 5].median()
        late_avg = player.iloc[-n // 5 :].median()
        growth_score = (late_avg - early_avg) / (range_ + epsilon)
        growth_score = min(max(growth_score, 0), 1)  # Clamp between 0 and 1

        # Final weighted consistency score (weights can be adjusted for best results)
        score = (
            0.3 * ahead_ratio  # External dominance
            + 0.25 * above_own_avg  # Internal consistency
            + 0.2 * stability  # Smooth momentum
            + 0.25 * growth_score  # Builds toward peak
        ) * 10

        return round(score, 2)


    def identify_key_moments(self, df: pd.DataFrame, threshold: float = 2.0) -> dict[str, Any]:
        """Identify key momentum shifts in the match."""
        key_moments = {"momentum_shifts": [], "peak_moments": [], "turning_points": []}

        if "P1Momentum" in df.columns and "P2Momentum" in df.columns:
            momentum_diff = df["P1Momentum"] - df["P2Momentum"]
            momentum_change = momentum_diff.diff().abs()

            # Find significant momentum shifts
            significant_shifts = df[momentum_change > momentum_change.median() * threshold]

            for idx, row in significant_shifts.iterrows():
                key_moments["momentum_shifts"].append(
                    {
                        "point_number": row.get("PointNumber", idx),
                        "time": row.get("cumulative_seconds", 0),
                        "momentum_change": momentum_change.loc[idx],
                        "p1_momentum": row["P1Momentum"],
                        "p2_momentum": row["P2Momentum"],
                    },
                )

            # Find peak momentum moments
            p1_peaks = df[df["P1Momentum"] == df["P1Momentum"].max()]
            p2_peaks = df[df["P2Momentum"] == df["P2Momentum"].max()]

            for idx, row in p1_peaks.iterrows():
                key_moments["peak_moments"].append(
                    {
                        "player": row.get("player1", "Player 1"),
                        "point_number": row.get("PointNumber", idx),
                        "momentum": row["P1Momentum"],
                    },
                )

            for idx, row in p2_peaks.iterrows():
                key_moments["peak_moments"].append(
                    {
                        "player": row.get("player2", "Player 2"),
                        "point_number": row.get("PointNumber", idx),
                        "momentum": row["P2Momentum"],
                    },
                )

        return key_moments
