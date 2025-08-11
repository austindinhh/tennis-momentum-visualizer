"""Data processing functions for tennis match analysis."""

from typing import Any

import polars as pl

from src.utils import calculate_match_score, load_config, parse_time_to_seconds


class DataProcessor:
    """Handles data processing and transformation for tennis matches."""

    def __init__(self, config_path: str | None = None) -> None:
        self.config = load_config(config_path)
        self._columns: set[str] | None = None


    def _cache_columns(self, df: pl.LazyFrame) -> None:
        """Cache column names for future use."""
        if self._columns is None:
            self._columns = set(df.collect_schema().names())


    def process_match_data(self, df: pl.LazyFrame | pl.DataFrame, animation_type: str = "Time-based") -> dict[str, Any]:
        """Process the match data for visualization."""
        if isinstance(df, pl.DataFrame):
            df = df.lazy()

        # Cache columns once at the start of processing
        self._cache_columns(df)

        df = df.with_columns(
            pl.col("ElapsedTime").map_elements(parse_time_to_seconds, return_dtype=pl.Int64).alias("cumulative_seconds"),
            pl.col("PointNumber").cast(pl.Int64),
            pl.col("P1Momentum").cast(pl.Float64).fill_null(0),
            pl.col("P2Momentum").cast(pl.Float64).fill_null(0),
        )

        # Choose x-axis based on animation type
        if animation_type == "Time-based":
            df = df.with_columns(pl.col("cumulative_seconds").alias("x_axis"))
            x_label = "Elapsed Time (seconds)"
        else:
            df = df.with_columns(pl.col("PointNumber").alias("x_axis"))
            x_label = "Point Number"

        # Calculate stats
        match_stats = self._calculate_match_statistics(df, x_label, animation_type)

        return {"df": df, "stats": match_stats}


    def _calculate_match_statistics(self, df: pl.LazyFrame, x_label: str, animation_type: str) -> dict[str, Any]:
        """Calculate comprehensive match statistics."""
        collected = df.select(
            pl.count().alias("total_points"),
            pl.max("cumulative_seconds").alias("match_duration"),
            pl.first("player1").alias("player1_name"),
            pl.first("player2").alias("player2_name"),
        ).collect().to_dict(as_series=False)

        stats = {
            "total_points": collected["total_points"][0],
            "match_duration": collected["match_duration"][0] or 0,
            "player1_name": collected["player1_name"][0] or "Player 1",
            "player2_name": collected["player2_name"][0] or "Player 2",
            "x_label": x_label,
            "animation_type": animation_type,
        }

        try:
            final_score, winner, p1_sets, p2_sets = calculate_match_score(df)
            stats.update({"final_score": final_score, "winner": winner, "p1_sets": p1_sets, "p2_sets": p2_sets})
        except Exception:
            stats.update({"final_score": "Score unavailable", "winner": "Unknown", "p1_sets": 0, "p2_sets": 0})

        stats.update(self._calculate_momentum_stats(df))
        stats.update(self._calculate_set_breakdown(df))

        return stats


    def _calculate_momentum_stats(self, df: pl.LazyFrame) -> dict[str, Any]:
        """Calculate momentum-related statistics."""
        if not {"P1Momentum", "P2Momentum"}.issubset(self._columns):
            return {}

        momentum_diff = (pl.col("P1Momentum") - pl.col("P2Momentum"))
        momentum_swings = momentum_diff.diff().abs().fill_null(0)
        median_swings = momentum_swings.median()

        collected = df.select(
            pl.median("P1Momentum").alias("p1_avg_momentum"),
            pl.median("P2Momentum").alias("p2_avg_momentum"),
            pl.max("P1Momentum").alias("p1_max_momentum"),
            pl.max("P2Momentum").alias("p2_max_momentum"),
            pl.min("P1Momentum").alias("p1_min_momentum"),
            pl.min("P2Momentum").alias("p2_min_momentum"),
            (momentum_swings > median_swings).sum().alias("momentum_swings"),
            (pl.col("P1Momentum") > pl.col("P2Momentum")).sum().alias("p1_dominant_points"),
            (pl.col("P2Momentum") > pl.col("P1Momentum")).sum().alias("p2_dominant_points"),
        ).collect()

         # Unpack all single-element lists into scalars
        stats = {k: v[0] for k, v in collected.to_dict(as_series=False).items()}

        p1_dom = collected["p1_dominant_points"][0]
        p2_dom = collected["p2_dominant_points"][0]
        total_points = df.select(pl.count()).collect().item()

        stats.update({
            "p1_dominance_pct": (p1_dom / total_points) * 100,
            "p2_dominance_pct": (p2_dom / total_points) * 100,
            })

        return stats


    def _calculate_set_breakdown(self, df: pl.LazyFrame) -> dict[str, Any]:
        """Calculate set-by-set statistics."""
        if "SetNo" not in self._columns:
            return {"set_breakdown": [], "total_sets": 0}

        set_numbers = df.select(pl.col("SetNo").unique()).collect().to_series().to_list()
        set_breakdown = []

        # Pre-determine which optional columns exist
        has_games_won = {"P1GamesWon", "P2GamesWon"}.issubset(self._columns)
        has_momentum = {"P1Momentum", "P2Momentum"}.issubset(self._columns)

        for set_no in sorted(set_numbers):
            set_df = df.filter(pl.col("SetNo") == set_no)

            # Build select expressions based on available columns
            select_exprs = [
                pl.count().alias("points_played"),
                (pl.max("cumulative_seconds") - pl.min("cumulative_seconds")).alias("duration"),
            ]

            if has_games_won:
                select_exprs.extend([
                    pl.last("P1GamesWon").alias("p1_games"),
                    pl.last("P2GamesWon").alias("p2_games"),
                ])

            if has_momentum:
                select_exprs.extend([
                    pl.median("P1Momentum").alias("p1_avg_momentum"),
                    pl.median("P2Momentum").alias("p2_avg_momentum"),
                ])

            collected = set_df.select(select_exprs).collect()

            set_info = {k: (v[0] if isinstance(v, list) else v) for k, v in collected.to_dict(as_series=False).items()}
            set_info["set_number"] = int(set_no)
            set_breakdown.append(set_info)

        return {"set_breakdown": set_breakdown, "total_sets": len(set_breakdown)}


    def smooth_momentum_data(self, df: pl.LazyFrame, window_size: int | None = None) -> pl.LazyFrame:
        """Apply smoothing to momentum data."""
        if window_size is None:
            window_size = self.config.get("visualization", {}).get("momentum", {}).get("window_size", 5)

        if {"P1Momentum", "P2Momentum"}.issubset(self._columns):
            df = df.with_columns([
                pl.col("P1Momentum").rolling_mean(window_size, center=True).fill_null(pl.col("P1Momentum")).alias("P1Momentum"),
                pl.col("P2Momentum").rolling_mean(window_size, center=True).fill_null(pl.col("P2Momentum")).alias("P2Momentum"),
            ])
        return df


    def calculate_momentum_derivatives(self, df: pl.LazyFrame) -> pl.LazyFrame:
        """Calculate momentum change rates and acceleration."""
        if {"P1Momentum", "P2Momentum"}.issubset(self._columns):
            df = df.with_columns([
                pl.col("P1Momentum").diff().fill_null(0).alias("P1Momentum_change"),
                pl.col("P2Momentum").diff().fill_null(0).alias("P2Momentum_change"),
            ])
            df = df.with_columns([
                pl.col("P1Momentum_change").diff().fill_null(0).alias("P1Momentum_accel"),
                pl.col("P2Momentum_change").diff().fill_null(0).alias("P2Momentum_accel"),
            ])
        return df


    def calculate_momentum_consistency(self, player: pl.Series, opponent: pl.Series, epsilon: float = 1e-6) -> float:
        """Calculate a consistency score for a player's momentum over a match."""
        ahead_ratio = (player > opponent).mean()
        avg = player.median()
        above_own_avg = (player > avg).mean()

        std_dev = player.std()
        range_ = player.max() - player.min()
        stability = 1 - (std_dev / (range_ + epsilon))

        n = len(player)
        early_avg = player[: n // 5].mean()
        late_avg = player[-n // 5 :].mean()
        growth_score = (late_avg - early_avg) / (range_ + epsilon)
        growth_score = min(max(growth_score, 0), 1)

        return round(
            (0.3 * ahead_ratio + 0.25 * above_own_avg + 0.2 * stability + 0.25 * growth_score) * 10, 2,
        )


    def identify_key_moments(self, df: pl.LazyFrame, threshold: float = 2.0) -> dict[str, Any]:
        """Identify key momentum shifts in the match."""
        key_moments = {"momentum_shifts": [], "peak_moments": [], "turning_points": []}

         # Calculate momentum difference & change
        df = df.with_columns([
            (pl.col("P1Momentum") - pl.col("P2Momentum")).alias("momentum_diff"),
            (pl.col("P1Momentum") - pl.col("P2Momentum")).diff().abs().alias("momentum_change")])

        # Compute median of momentum_change
        median_change = df.select(pl.col("momentum_change").median()).collect()[0, 0]
        shift_threshold = median_change * threshold

        # Find significant momentum shifts
        significant_shifts = (df.filter(pl.col("momentum_change") > shift_threshold).collect())

        for row in significant_shifts.iter_rows(named=True):
            key_moments["momentum_shifts"].append(
                {
                    "point_number": row.get("PointNumber", None),
                    "time": row.get("cumulative_seconds", 0),
                    "momentum_change": row["momentum_change"],
                    "p1_momentum": row["P1Momentum"],
                    "p2_momentum": row["P2Momentum"],
                },
            )

        # Peak momentum moments
        collected_df = df.collect()
        p1_max = collected_df["P1Momentum"].max()
        p2_max = collected_df["P2Momentum"].max()

        p1_peaks = collected_df.filter(pl.col("P1Momentum") == p1_max)
        p2_peaks = collected_df.filter(pl.col("P2Momentum") == p2_max)

        for row in p1_peaks.iter_rows(named=True):
            key_moments["peak_moments"].append(
                {
                    "player": row.get("player1", "Player 1"),
                    "point_number": row.get("PointNumber", None),
                    "momentum": row["P1Momentum"],
                },
            )

        for row in p2_peaks.iter_rows(named=True):
            key_moments["peak_moments"].append(
                {
                    "player": row.get("player2", "Player 2"),
                    "point_number": row.get("PointNumber", None),
                    "momentum": row["P2Momentum"],
                },
            )

        return key_moments
