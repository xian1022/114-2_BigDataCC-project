import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.analysis.analyze_data import (
    get_extreme_values,
    get_monthly_average,
    get_station_statistics,
    get_summary_statistics,
)
from src.analysis.clean_data import REQUIRED_COLUMNS, clean_ocean_data, save_cleaned_data
from src.app.gradio_app import (
    CHART_CHOICES,
    COLUMN_LABELS,
    DATA_SOURCE_CHOICES,
    STATION_CHOICES,
    normalize_chart_type,
    normalize_column,
    normalize_data_source,
    normalize_station,
    build_app,
    update_dashboard,
)
from src.utils.data_loader import load_sample_data, load_uploaded_data


class OceanDashboardCoreTest(unittest.TestCase):
    def test_clean_ocean_data_handles_missing_values_duplicates_and_invalid_dates(self):
        df = pd.DataFrame(
            [
                {
                    "date": "2026-03-01",
                    "station": "Keelung",
                    "sea_temperature_c": "22.1",
                    "tide_level_m": "1.2",
                    "wave_height_m": None,
                    "wind_speed_mps": "5.1",
                    "salinity_psu": "33.4",
                },
                {
                    "date": "bad-date",
                    "station": "Taichung",
                    "sea_temperature_c": "bad",
                    "tide_level_m": "1.0",
                    "wave_height_m": "0.8",
                    "wind_speed_mps": "4.0",
                    "salinity_psu": "32.9",
                },
                {
                    "date": "2026-03-01",
                    "station": "Keelung",
                    "sea_temperature_c": "22.1",
                    "tide_level_m": "1.2",
                    "wave_height_m": None,
                    "wind_speed_mps": "5.1",
                    "salinity_psu": "33.4",
                },
                {
                    "date": "2026-03-02",
                    "station": None,
                    "sea_temperature_c": "23.0",
                    "tide_level_m": None,
                    "wave_height_m": "1.1",
                    "wind_speed_mps": "6.2",
                    "salinity_psu": "33.2",
                },
            ]
        )

        cleaned = clean_ocean_data(df)

        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned.iloc[1]["station"], "Unknown")
        self.assertFalse(cleaned[REQUIRED_COLUMNS].isna().any().any())
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned["date"]))

    def test_analysis_functions_return_gradio_friendly_results(self):
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-03-01", "2026-03-02", "2026-04-01"]),
                "station": ["Keelung", "Keelung", "Taichung"],
                "sea_temperature_c": [22.0, 24.0, 26.0],
                "tide_level_m": [1.1, 1.4, 1.2],
                "wave_height_m": [0.7, 0.9, 1.0],
                "wind_speed_mps": [5.0, 5.5, 4.0],
                "salinity_psu": [33.1, 33.2, 32.8],
            }
        )

        summary = get_summary_statistics(df)
        station_stats = get_station_statistics(df)
        monthly = get_monthly_average(df, "sea_temperature_c")
        extremes = get_extreme_values(df, "sea_temperature_c")

        self.assertIn("mean", summary.index)
        self.assertIn("Keelung", station_stats["station"].values)
        self.assertEqual(monthly.loc[0, "month"], "2026-03")
        self.assertIn("Maximum", extremes["type"].values)
        self.assertIn("Minimum", extremes["type"].values)

    def test_data_loader_reads_sample_and_uploaded_csv(self):
        sample = load_sample_data()
        self.assertTrue(set(REQUIRED_COLUMNS).issubset(sample.columns))

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8") as tmp:
            tmp.write(",".join(REQUIRED_COLUMNS) + "\n")
            tmp.write("2026-03-01,Keelung,22.1,1.2,0.8,5.1,33.4\n")
            temp_path = tmp.name

        uploaded = load_uploaded_data(temp_path)
        Path(temp_path).unlink(missing_ok=True)

        self.assertEqual(len(uploaded), 1)
        self.assertEqual(uploaded.loc[0, "station"], "Keelung")

    def test_save_cleaned_data_writes_processed_file(self):
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-03-01"]),
                "station": ["Keelung"],
                "sea_temperature_c": [22.0],
                "tide_level_m": [1.1],
                "wave_height_m": [0.7],
                "wind_speed_mps": [5.0],
                "salinity_psu": [33.1],
            }
        )

        path = save_cleaned_data(df)
        self.assertTrue(Path(path).exists())

    def test_chinese_ui_choices_map_to_internal_values(self):
        self.assertIn("範例資料", DATA_SOURCE_CHOICES)
        self.assertIn("全部測站", STATION_CHOICES)
        self.assertIn("趨勢折線圖", CHART_CHOICES)
        self.assertIn("海溫（°C）", COLUMN_LABELS)

        self.assertEqual(normalize_data_source("上傳 CSV"), "Upload CSV")
        self.assertEqual(normalize_column("海溫（°C）"), "sea_temperature_c")
        self.assertEqual(normalize_station("基隆"), "Keelung")
        self.assertEqual(normalize_chart_type("測站平均長條圖"), "Station Average Bar Chart")

    def test_dashboard_returns_chinese_status_and_display_columns(self):
        raw, cleaned, summary, station_stats, chart, main_chart, status = update_dashboard(
            "範例資料",
            None,
            "海溫（°C）",
            "全部測站",
            "趨勢折線圖",
        )

        self.assertIn("資料載入成功", status)
        self.assertIn("原始資料", status)
        self.assertIn("日期", raw.columns)
        self.assertIn("測站", cleaned.columns)
        self.assertIn("平均值", summary.index)
        self.assertIn("測站", station_stats.columns)
        self.assertEqual(type(chart).__name__, "Figure")
        self.assertEqual(type(main_chart).__name__, "Figure")

    def test_dashboard_has_main_chart_visible_without_switching_tabs(self):
        app = build_app()
        labels = [
            component.get("props", {}).get("label")
            for component in app.config.get("components", [])
        ]

        self.assertIn("主要圖表", labels)


if __name__ == "__main__":
    unittest.main()
