from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "date",
    "station",
    "sea_temperature_c",
    "tide_level_m",
    "wave_height_m",
    "wind_speed_mps",
    "salinity_psu",
]

NUMERIC_COLUMNS = [
    "sea_temperature_c",
    "tide_level_m",
    "wave_height_m",
    "wind_speed_mps",
    "salinity_psu",
]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def validate_required_columns(df: pd.DataFrame) -> None:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        available = ", ".join(df.columns.astype(str))
        missing = ", ".join(missing_columns)
        raise ValueError(
            f"CSV is missing required columns: {missing}. Available columns: {available}"
        )


def clean_ocean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean ocean observation data for dashboard analysis."""
    if df is None or df.empty:
        raise ValueError("Input data is empty. Please provide a CSV with ocean data.")

    validate_required_columns(df)
    cleaned = df[REQUIRED_COLUMNS].copy()

    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned = cleaned.dropna(subset=["date"])

    cleaned["station"] = cleaned["station"].fillna("Unknown").astype(str).str.strip()
    cleaned.loc[cleaned["station"] == "", "station"] = "Unknown"

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        mean_value = cleaned[column].mean()
        fill_value = 0 if pd.isna(mean_value) else mean_value
        cleaned[column] = cleaned[column].fillna(fill_value)

    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.sort_values(["date", "station"]).reset_index(drop=True)

    if cleaned.empty:
        raise ValueError("No valid rows remain after cleaning. Please check the CSV format.")

    return cleaned


def save_cleaned_data(df: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    """Save cleaned data to data/processed/cleaned_ocean_data.csv."""
    if output_path is None:
        output_path = _project_root() / "data" / "processed" / "cleaned_ocean_data.csv"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    return output_path
