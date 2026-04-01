"""
rolling_monitor_transit_miller.py - Project script.

Author: Daniel Miller
Date: 2026-03

Time-Series System Metrics Data

- Data is taken from a system that records transit rides by day
- Each row represents one observation at a specific day
- The CSV file includes these columns:
  - day: when the observation occurred
  - rides: number of transit rides taken


Purpose

- Read time-series transit rides from a CSV file.
- Demonstrate rolling monitoring using a moving window.
- Compute rolling averages to smooth short-term variation.
- Save the resulting monitoring signals as a CSV artifact.
- Log the pipeline process to assist with debugging and transparency.

Questions to Consider

- How does transit behavior change over time?
- Why might a rolling average reveal patterns that individual observations hide?
- How can smoothing short-term variation help us understand longer-term trends?

Paths (relative to repo root)

    INPUT FILE: data/transit_ridership.csv
    OUTPUT FILE: artifacts/rolling_metrics_transit_miller.csv

Terminal command to run this file from the root project folder

    uv run python -m cintel.rolling_monitor_transit_miller

"""
# === DECLARE IMPORTS ===

import logging
from pathlib import Path
from typing import Final

import matplotlib.pyplot as plt
import polars as pl
from datafun_toolkit.logger import get_logger, log_header, log_path

# === CONFIGURE LOGGER ===

LOG: logging.Logger = get_logger("P5", level="DEBUG")

# === DEFINE GLOBAL PATHS ===

ROOT_DIR: Final[Path] = Path.cwd()
DATA_DIR: Final[Path] = ROOT_DIR / "data"
ARTIFACTS_DIR: Final[Path] = ROOT_DIR / "artifacts"

DATA_FILE: Final[Path] = DATA_DIR / "transit_ridership.csv"
OUTPUT_FILE: Final[Path] = ARTIFACTS_DIR / "rolling_metrics_transit_miller.csv"

# === DEFINE THE MAIN FUNCTION ===


def main() -> None:
    """Run the pipeline.

    log_header() logs a standard run header.
    log_path() logs repo-relative paths (privacy-safe).
    """
    log_header(LOG, "CINTEL")

    LOG.info("========================")
    LOG.info("START main()")
    LOG.info("========================")

    log_path(LOG, "ROOT_DIR", ROOT_DIR)
    log_path(LOG, "DATA_FILE", DATA_FILE)
    log_path(LOG, "OUTPUT_FILE", OUTPUT_FILE)

    # Ensure artifacts directory exists
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    log_path(LOG, "ARTIFACTS_DIR", ARTIFACTS_DIR)

    # ----------------------------------------------------
    # STEP 1: READ CSV DATA FILE INTO A POLARS DATAFRAME (TABLE)
    # ----------------------------------------------------
    df = pl.read_csv(DATA_FILE)

    LOG.info(f"Loaded {df.height} time-series records")

    # ----------------------------------------------------
    # STEP 2: SORT DATA BY DAY
    # ----------------------------------------------------
    # Time-series analysis requires observations to be ordered.
    df = df.sort("day")

    LOG.info("Sorted records by day")

    # ----------------------------------------------------
    # STEP 3: DEFINE ROLLING WINDOW RECIPES
    # ----------------------------------------------------
    # A rolling window computes statistics over the most recent
    # N observations. The window "moves" forward one row at a time.

    # Example: if WINDOW_SIZE = 3
    # row 1 → mean of rows [1]
    # row 2 → mean of rows [1,2]
    # row 3 → mean of rows [1,2,3]
    # row 4 → mean of rows [2,3,4]

    WINDOW_SIZE: int = 5

    # ----------------------------------------------------
    # STEP 3.1: DEFINE ROLLING MEAN FOR # OF RIDES
    # ----------------------------------------------------
    # The `rides` column holds the count of transit rides taken at each day.
    rides_rolling_mean_recipe: pl.Expr = (
        pl.col("rides").rolling_mean(WINDOW_SIZE).alias("rides_rolling_mean")
    )

    # ----------------------------------------------------
    # STEP 3.2: DEFINE ROLLING STD DEV FOR # OF RIDES
    # ----------------------------------------------------
    # The `rides` column holds the count of transit rides taken at each day.
    rides_rolling_std_dev_recipe: pl.Expr = (
        pl.col("rides").rolling_std(WINDOW_SIZE).alias("rides_rolling_std_dev")
    )

    # ----------------------------------------------------
    # STEP 3.3: DEFINE ROLLING SUM FOR # OF RIDES
    # ----------------------------------------------------
    # The `rides` column holds the count of transit rides taken at each day.
    rides_rolling_sum_recipe: pl.Expr = (
        pl.col("rides").rolling_sum(WINDOW_SIZE).alias("rides_rolling_sum")
    )

    # ----------------------------------------------------
    # STEP 3.4: DEFINE ROLLING COEFFICIENT OF VARIATION FOR # OF RIDES
    # ----------------------------------------------------
    # The `rides` column holds the count of transit rides taken at each day.
    rides_rolling_coeff_var_recipe: pl.Expr = (
        pl.col("rides").rolling_std(WINDOW_SIZE)
        / pl.col("rides").rolling_mean(WINDOW_SIZE)
    ).alias("rides_rolling_coeff_var")

    # ----------------------------------------------------
    # STEP 3.5: APPLY THE ROLLING RECIPES IN A NEW DATAFRAME
    # ----------------------------------------------------
    # with_columns() evaluates the recipes and adds the new columns
    df_with_rolling = df.with_columns(
        [
            rides_rolling_sum_recipe,
            rides_rolling_mean_recipe,
            rides_rolling_std_dev_recipe,
            rides_rolling_coeff_var_recipe,
        ]
    )

    LOG.info("Computed rolling signals")

    # ----------------------------------------------------
    # STEP 4: SAVE RESULTS AS AN ARTIFACT
    # ----------------------------------------------------
    df_with_rolling.write_csv(OUTPUT_FILE)
    LOG.info(f"Wrote rolling monitoring file: {OUTPUT_FILE}")

    LOG.info("========================")
    LOG.info("Pipeline executed successfully!")
    LOG.info("========================")

    # ----------------------------------------------------
    # STEP 5: PLOT COEFFICIENT OF VARIATION OVER TIME
    # ----------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Primary axis (rolling mean)
    ax1.plot(
        df_with_rolling["day"],
        df_with_rolling["rides_rolling_mean"],
        label="Rolling Mean",
        color="blue",
    )
    ax1.set_xlabel("Day")
    ax1.set_ylabel("Rolling Mean of Rides", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    # Secondary axis (coefficient of variation)
    ax2 = ax1.twinx()
    ax2.plot(
        df_with_rolling["day"],
        df_with_rolling["rides_rolling_coeff_var"],
        label="Rolling Coeff of Var",
        color="red",
    )
    ax2.set_ylabel("Rolling Coefficient of Variation", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    plt.title("Rolling Mean vs Coefficient of Variation")
    plt.tight_layout()
    plt.savefig(ARTIFACTS_DIR / "rolling_plot_transit_miller.png")
    plt.show()

    LOG.info("END main()")


# === CONDITIONAL EXECUTION GUARD ===

if __name__ == "__main__":
    main()
