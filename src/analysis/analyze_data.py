import numpy as np
import pandas as pd

from src.analysis.clean_data import NUMERIC_COLUMNS


def _validate_column(df: pd.DataFrame, column: str) -> None:
    if column not in df.columns:
        available = ", ".join(df.columns.astype(str))
        raise ValueError(f"Column '{column}' does not exist. Available columns: {available}")
    if column not in NUMERIC_COLUMNS:
        supported = ", ".join(NUMERIC_COLUMNS)
        raise ValueError(f"Column '{column}' is not supported. Supported columns: {supported}")


def get_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return overall descriptive statistics for numeric ocean variables."""
    if df.empty:
        raise ValueError("Cannot analyze empty data.")
    summary = df[NUMERIC_COLUMNS].describe().round(3)
    summary.loc["range"] = np.ptp(df[NUMERIC_COLUMNS].to_numpy(dtype=float), axis=0).round(3)
    summary.loc["variance"] = np.var(df[NUMERIC_COLUMNS].to_numpy(dtype=float), axis=0).round(3)
    return summary


def get_station_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return mean, min, and max values grouped by station."""
    if df.empty:
        raise ValueError("Cannot analyze empty data.")

    grouped = df.groupby("station")[NUMERIC_COLUMNS].agg(["mean", "min", "max"]).round(3)
    grouped.columns = [f"{column}_{stat}" for column, stat in grouped.columns]
    return grouped.reset_index()


def get_monthly_average(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return monthly average for a selected numeric column."""
    _validate_column(df, column)
    monthly_df = df.copy()
    monthly_df["date"] = pd.to_datetime(monthly_df["date"], errors="coerce")
    monthly_df = monthly_df.dropna(subset=["date"])
    monthly_df["month"] = monthly_df["date"].dt.to_period("M").astype(str)
    return (
        monthly_df.groupby("month", as_index=False)[column]
        .mean()
        .rename(columns={column: f"avg_{column}"})
        .round(3)
    )


def get_extreme_values(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return rows containing the maximum and minimum value for a selected column."""
    _validate_column(df, column)
    if df.empty:
        raise ValueError("Cannot analyze empty data.")

    max_idx = df[column].idxmax()
    min_idx = df[column].idxmin()
    rows = df.loc[[max_idx, min_idx], ["date", "station", column]].copy()
    rows.insert(0, "type", ["Maximum", "Minimum"])
    rows["date"] = pd.to_datetime(rows["date"]).dt.strftime("%Y-%m-%d")
    return rows.reset_index(drop=True)
