from pathlib import Path
from typing import Any

import pandas as pd


def get_project_root() -> Path:
    """Return the project root so paths work in local and Docker environments."""
    return Path(__file__).resolve().parents[2]


def load_sample_data() -> pd.DataFrame:
    """Load the built-in sample ocean CSV."""
    sample_path = get_project_root() / "data" / "raw" / "sample_ocean_data.csv"
    if not sample_path.exists():
        raise FileNotFoundError(f"Sample data not found: {sample_path}")
    return pd.read_csv(sample_path)


def load_uploaded_data(file: Any) -> pd.DataFrame:
    """Load a user-uploaded CSV from a Gradio file object or path."""
    if file is None:
        raise ValueError("No uploaded file found. Please upload a CSV or choose Sample Data.")

    file_path = getattr(file, "name", file)
    if not file_path:
        raise ValueError("Uploaded file path is invalid.")

    try:
        return pd.read_csv(file_path)
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="utf-8-sig")
    except Exception as exc:
        raise ValueError(f"Could not read uploaded CSV: {exc}") from exc
