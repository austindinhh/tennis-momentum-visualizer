"""Main tennis match momentum logic."""

import os
import shutil
import tempfile

import polars as pl
import requests

from src.utils import load_config, validate_player_names, validate_year


class TennisMatchAnalyzer:
    """Core analyzer for tennis match momentum."""

    def __init__(self, config_path: str | None = None) -> None:
        self.config = load_config(config_path)
        self.temp_dir = None
        self.tournament_url = None
        self.tournament_name = None
        self.year = None
        self.player1 = None
        self.player2 = None
        self.points_file = None
        self.matches_file = None


    def download_tournament_data(self, tournament_url: str, year: int) -> bool:
        """Download tournament data for the specified year."""
        if not validate_year(year, self.config):
            msg = f"Year {year} is not supported"
            raise ValueError(msg)

        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()

        # Base URL
        base_url = "https://raw.githubusercontent.com/JeffSackmann/tennis_slam_pointbypoint/master"

        # Download both points and matches files
        success = True

        # Download points data
        points_filename = f"{year}-{tournament_url}-points.csv"
        points_url = f"{base_url}/{points_filename}"

        if not self._download_file(points_url, points_filename):
            success = False
        else:
            self.points_file = os.path.join(self.temp_dir, points_filename)

        # Download matches data
        matches_filename = f"{year}-{tournament_url}-matches.csv"
        matches_url = f"{base_url}/{matches_filename}"

        if not self._download_file(matches_url, matches_filename):
            success = False
        else:
            self.matches_file = os.path.join(self.temp_dir, matches_filename)

        return success


    def _download_file(self, url: str, filename: str) -> bool:
        """Download a single file."""
        try:
            timeout = self.config.get("data", {}).get("download_timeout", 30)
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            # Save to temporary directory
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, "wb") as f:
                f.write(response.content)

            return True

        except requests.RequestException:
            return False


    def find_match_id(self, player1: str, player2: str) -> str | None:
        """Find match ID for the specified players."""
        if not self.temp_dir or not self.matches_file:
            return None

        if not os.path.exists(self.matches_file):
            return None

        try:
            # Normalize player names for comparison
            p1 = player1.lower().strip()
            p2 = player2.lower().strip()

            # Find matches with these players and return only the match id
            matches = (
                pl.scan_csv(self.matches_file)
                .filter(
                    pl.col("player1").str.to_lowercase().str.contains(p1)
                    & pl.col("player2").str.to_lowercase().str.contains(p2)
                    | pl.col("player1").str.to_lowercase().str.contains(p2)
                    & pl.col("player2").str.to_lowercase().str.contains(p1),
                )
                .select("match_id")
                .first()
                .collect()
                .item()
            )

            if matches:
                return matches
            else:
                return None

        except Exception:
            return None


    def create_match_dataframe(self, match_id: str) -> pl.DataFrame | None:
        """Create a dataframe for the specific match."""
        if not self.temp_dir or not self.points_file:
            return None

        if not os.path.exists(self.points_file):
            return None

        try:
            # Filter for the specific match
            df_match = (
                pl.scan_csv(self.points_file, infer_schema_length=10000)
                .filter(pl.col("match_id") == match_id)
                .filter((pl.col("PointNumber") != "0Y") & (pl.col("PointNumber") != "0X"))
                .join(pl.scan_csv(self.matches_file).filter(pl.col("match_id") == match_id), on="match_id")
                .select(
                    [
                        "match_id",
                        "player1",
                        "player2",
                        "ElapsedTime",
                        "PointNumber",
                        "P1Momentum",
                        "P2Momentum",
                        "SetNo",
                        "P1GamesWon",
                        "P2GamesWon",
                    ],
                )
                .collect()
            )

            if df_match.height == 0:
                return None

            # Add momentum calculations
            # df_match = self._calculate_momentum(df_match)

            return df_match

        except Exception as e:
            print(f"Error creating match dataframe: {e}")
            return None


    def _calculate_momentum(self, df: pl.DataFrame) -> pl.DataFrame:
        """Calculate momentum for both players."""
        # Sort by point number to ensure correct order
        df = df.sort("PointNumber")

        # Initialize momentum columns
        momentum_data = []
        p1_momentum = 0.0
        p2_momentum = 0.0

        # Get momentum calculation parameters
        decay_factor = self.config.get("analysis", {}).get("momentum_calculation", {}).get("decay_factor", 0.95)
        base_weight = self.config.get("analysis", {}).get("momentum_calculation", {}).get("base_weight", 1.0)  # noqa: F841
        recent_weight = self.config.get("analysis", {}).get("momentum_calculation", {}).get("recent_weight", 1.5)

        for row in df.iter_rows():
            # Apply decay to existing momentum
            p1_momentum *= decay_factor
            p2_momentum *= decay_factor

            # Extract point winner information (this would need to be adapted based on actual data structure)
            # For now, using a simplified approach
            point_winner = row[df.columns.index("PointWinner")] if "PointWinner" in df.columns else 1

            # Update momentum based on point winner
            if point_winner == 1:
                p1_momentum += recent_weight
            elif point_winner == 2:
                p2_momentum += recent_weight

            momentum_data.append({"P1Momentum": p1_momentum, "P2Momentum": p2_momentum})

        # Add momentum columns to dataframe
        momentum_df = pl.DataFrame(momentum_data)
        return df.with_columns([momentum_df["P1Momentum"], momentum_df["P2Momentum"]])


    def get_file_paths(self) -> dict[str, str]:
        """Return the paths to downloaded files."""
        return {"points": self.points_file, "matches": self.matches_file}


    def cleanup_files(self) -> None:
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            self.points_file = None
            self.matches_file = None


    def get_available_tournaments(self) -> dict[str, str]:
        """Get available tournaments from config."""
        tournaments = self.config.get("tournaments", {})
        return {v["name"]: k for k, v in tournaments.items()}


    def get_supported_years(self) -> tuple:
        """Get supported year range."""
        years = self.config.get("data", {}).get("supported_years", {})
        return years.get("min", 2011), years.get("max", 2024)


    def validate_inputs(self, tournament_url: str, year: int, player1: str, player2: str) -> tuple:
        """Validate all inputs for analysis."""
        # Check tournament
        tournaments = self.config.get("tournaments", {})
        if tournament_url not in [v["url"] for v in tournaments.values()]:
            return False, f"Invalid tournament: {tournament_url}"

        # Check year
        if not validate_year(year, self.config):
            min_year, max_year = self.get_supported_years()
            return False, f"Year must be between {min_year} and {max_year}"

        # Check player names
        valid, message = validate_player_names(player1, player2)
        if not valid:
            return False, message

        return True, "All inputs valid"
