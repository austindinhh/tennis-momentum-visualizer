"""Utility functions for tennis match analysis."""

from pathlib import Path
import re
from typing import Any

import polars as pl
import yaml


def load_config(config_path: str | None = None) -> dict[str, Any]:
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"

    try:
        with open(config_path) as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        # Return default config if file not found
        return get_default_config()
    except yaml.YAMLError as e:
        msg = f"Error parsing config file: {e}"
        raise ValueError(msg)


def get_default_config() -> dict[str, Any]:
    """Return default configuration if config file is not available."""
    return {
        "tournaments": {
            "ausopen": {"name": "Australian Open", "url": "ausopen"},
            "frenchopen": {"name": "French Open", "url": "frenchopen"},
            "wimbledon": {"name": "Wimbledon", "url": "wimbledon"},
            "usopen": {"name": "US Open", "url": "usopen"},
        },
        "data": {
            "download_timeout": 30,
            "max_retries": 3,
            "cache_duration": 3600,
            "supported_years": {"min": 2011, "max": 2024},
        },
        "visualization": {
            "default_colors": {"player1": "#1f77b4", "player2": "#d62728"},
            "chart": {"height": 500, "line_width": 3, "marker_size": 4},
        },
        "ui": {
            "default_tournament": "wimbledon",
            "default_year": 2019,
            "default_players": {"player1": "Novak Djokovic", "player2": "Roger Federer"},
        },
    }


def format_time(seconds: int) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{int(hours):01d}:{int(minutes):02d}:{int(secs):02d}"


def parse_time_to_seconds(time_str: str) -> int:
    """Convert HH:MM:SS format to seconds."""
    try:
        parts = time_str.split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return int(parts[0])
    except (ValueError, IndexError):
        return 0


def validate_player_names(player1: str, player2: str) -> tuple[bool, str]:
    """Validate player name format."""
    if not player1.strip() or not player2.strip():
        return False, "Player names cannot be empty"

    # Check for reasonable name format (at least first and last name)
    name_pattern = r"^[A-Za-z\s\-\'\.]+$"

    if not re.match(name_pattern, player1.strip()):
        return False, f"Invalid characters in player 1 name: {player1}"

    if not re.match(name_pattern, player2.strip()):
        return False, f"Invalid characters in player 2 name: {player2}"

    # Check if names have at least two parts (first and last name)
    if len(player1.strip().split()) < 2:
        return False, "Player 1 name should include first and last name"

    if len(player2.strip().split()) < 2:
        return False, "Player 2 name should include first and last name"

    return True, "Valid names"


def validate_year(year: int, config: dict[str, Any]) -> bool:
    """Validate tournament year against supported range."""
    min_year = config.get("data", {}).get("supported_years", {}).get("min", 2011)
    max_year = config.get("data", {}).get("supported_years", {}).get("max", 2024)
    return min_year <= year <= max_year


def clean_filename(filename: str) -> str:
    """Clean filename for safe file system usage."""
    # Remove or replace invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove extra spaces and periods
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned.strip(".")


def ensure_directory(path: str) -> None:
    """Ensure directory exists, create if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_tournament_display_name(tournament_url: str, config: dict[str, Any]) -> str:
    """Get display name for tournament from URL."""
    tournaments = config.get("tournaments", {})
    for value in tournaments.values():
        if value.get("url") == tournament_url:
            return value.get("name", tournament_url.title())
    return tournament_url.title()


def calculate_match_score(df_lazy: pl.LazyFrame) -> tuple[str, str, int, int]:
    """Calculate final match score from dataframe."""
    df = df_lazy.collect()

    try:
        # Get set information
        sets = (
            df.group_by("SetNo")
            .agg([pl.col("P1GamesWon").last().alias("P1Games"), pl.col("P2GamesWon").last().alias("P2Games")])
            .sort("SetNo")
        )

        match_score = []
        p1_sets = p2_sets = 0

        for row in sets.iter_rows():
            set_no, p1_games, p2_games = row
            set_score = f"{int(p1_games)}-{int(p2_games)}"
            match_score.append(set_score)

            if p1_games > p2_games:
                p1_sets += 1
            elif p1_games < p2_games:
                p2_sets += 1

        score_str = ", ".join(match_score)
        winner = df["player1"][0] if p1_sets > p2_sets else df["player2"][0]

        return score_str, winner, p1_sets, p2_sets

    except Exception:
        return "Score unavailable", "Unknown", 0, 0
