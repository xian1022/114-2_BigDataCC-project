import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import gradio as gr

from src.analysis.analyze_data import (
    get_extreme_values,
    get_monthly_average,
    get_station_statistics,
    get_summary_statistics,
)
from src.analysis.clean_data import NUMERIC_COLUMNS, clean_ocean_data, save_cleaned_data
from src.utils.data_loader import load_sample_data, load_uploaded_data


plt.rcParams["font.sans-serif"] = [
    "Microsoft JhengHei",
    "Noto Sans CJK TC",
    "Noto Sans CJK SC",
    "SimHei",
    "Arial Unicode MS",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False

DATA_SOURCE_LABELS = {
    "範例資料": "Sample Data",
    "上傳 CSV": "Upload CSV",
    "Sample Data": "Sample Data",
    "Upload CSV": "Upload CSV",
}

COLUMN_LABELS = {
    "海溫（°C）": "sea_temperature_c",
    "潮位（公尺）": "tide_level_m",
    "浪高（公尺）": "wave_height_m",
    "風速（m/s）": "wind_speed_mps",
    "鹽度（PSU）": "salinity_psu",
}

STATION_LABELS = {
    "全部測站": "All Stations",
    "基隆": "Keelung",
    "台中": "Taichung",
    "高雄": "Kaohsiung",
    "花蓮": "Hualien",
    "台東": "Taitung",
    "All Stations": "All Stations",
    "Keelung": "Keelung",
    "Taichung": "Taichung",
    "Kaohsiung": "Kaohsiung",
    "Hualien": "Hualien",
    "Taitung": "Taitung",
}

CHART_LABELS = {
    "趨勢折線圖": "Trend Line Chart",
    "測站平均長條圖": "Station Average Bar Chart",
    "月份平均折線圖": "Monthly Average Line Chart",
    "Trend Line Chart": "Trend Line Chart",
    "Station Average Bar Chart": "Station Average Bar Chart",
    "Monthly Average Line Chart": "Monthly Average Line Chart",
}

COLUMN_DISPLAY_NAMES = {
    "date": "日期",
    "station": "測站",
    "sea_temperature_c": "海溫（°C）",
    "tide_level_m": "潮位（公尺）",
    "wave_height_m": "浪高（公尺）",
    "wind_speed_mps": "風速（m/s）",
    "salinity_psu": "鹽度（PSU）",
}

SUMMARY_INDEX_NAMES = {
    "count": "筆數",
    "mean": "平均值",
    "std": "標準差",
    "min": "最小值",
    "25%": "第 1 四分位數",
    "50%": "中位數",
    "75%": "第 3 四分位數",
    "max": "最大值",
    "range": "全距",
    "variance": "變異數",
}

STATION_DISPLAY_NAMES = {value: label for label, value in STATION_LABELS.items() if label in ["基隆", "台中", "高雄", "花蓮", "台東"]}

DATA_SOURCE_CHOICES = ["範例資料", "上傳 CSV"]
STATION_CHOICES = ["全部測站", "基隆", "台中", "高雄", "花蓮", "台東"]
CHART_CHOICES = ["趨勢折線圖", "測站平均長條圖", "月份平均折線圖"]

OCEAN_CSS = """
.gradio-container {
    background:
        radial-gradient(circle at 15% 0%, rgba(144, 224, 239, 0.45), transparent 28%),
        linear-gradient(180deg, #f0fbff 0%, #eef9f7 45%, #ffffff 100%);
}
.ocean-hero {
    border: 1px solid rgba(0, 119, 182, 0.16);
    border-radius: 8px;
    padding: 22px 24px;
    background: linear-gradient(135deg, rgba(0, 119, 182, 0.94), rgba(0, 180, 216, 0.88));
    color: #ffffff;
    box-shadow: 0 12px 30px rgba(0, 74, 112, 0.16);
}
.ocean-hero h1 {
    margin: 0 0 8px 0;
    color: #ffffff;
    letter-spacing: 0;
}
.ocean-hero p {
    margin: 0;
    color: rgba(255, 255, 255, 0.92);
}
.ocean-note {
    color: #0f4c5c;
    margin-top: 8px;
}
.gradio-container button.primary,
.gradio-container .gr-button-primary {
    background: linear-gradient(135deg, #0077b6, #00b4d8) !important;
    border-color: #0077b6 !important;
    color: white !important;
    font-weight: 700 !important;
}
.gradio-container button.primary:hover,
.gradio-container .gr-button-primary:hover {
    background: linear-gradient(135deg, #005f8f, #0096c7) !important;
}
.gradio-container .tabs button[aria-selected="true"] {
    color: #0077b6 !important;
    border-color: #00b4d8 !important;
}
"""

OCEAN_THEME = gr.themes.Soft(
    primary_hue="cyan",
    secondary_hue="blue",
    neutral_hue="slate",
    radius_size="sm",
)


def normalize_data_source(data_source: str) -> str:
    return DATA_SOURCE_LABELS.get(data_source, data_source)


def normalize_column(column: str) -> str:
    if column in COLUMN_LABELS:
        return COLUMN_LABELS[column]

    column_text = str(column)
    keyword_map = {
        "海溫": "sea_temperature_c",
        "潮位": "tide_level_m",
        "浪高": "wave_height_m",
        "風速": "wind_speed_mps",
        "鹽度": "salinity_psu",
    }
    for keyword, internal_column in keyword_map.items():
        if keyword in column_text:
            return internal_column
    return column


def normalize_station(station: str) -> str:
    return STATION_LABELS.get(station, station)


def normalize_chart_type(chart_type: str) -> str:
    return CHART_LABELS.get(chart_type, chart_type)


def _display_column_name(column: str) -> str:
    return COLUMN_DISPLAY_NAMES.get(column, column)


def _display_station_name(station: str) -> str:
    return STATION_DISPLAY_NAMES.get(station, station)


def _prepare_display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    display_df = df.copy()
    if "date" in display_df.columns:
        display_df["date"] = pd.to_datetime(display_df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    if "station" in display_df.columns:
        display_df["station"] = display_df["station"].map(_display_station_name).fillna(display_df["station"])
    return display_df.rename(columns=COLUMN_DISPLAY_NAMES)


def _prepare_summary_display(summary: pd.DataFrame) -> pd.DataFrame:
    display_df = summary.copy()
    display_df.index = [SUMMARY_INDEX_NAMES.get(str(index), str(index)) for index in display_df.index]
    display_df = display_df.rename(columns=COLUMN_DISPLAY_NAMES)
    return display_df


def _translate_station_stat_column(column: str) -> str:
    if column == "station":
        return "測站"

    suffix_names = {
        "_mean": "平均值",
        "_min": "最小值",
        "_max": "最大值",
    }
    for suffix, suffix_label in suffix_names.items():
        if column.endswith(suffix):
            base_column = column[: -len(suffix)]
            return f"{_display_column_name(base_column)} {suffix_label}"
    return column


def _prepare_station_stats_display(station_stats: pd.DataFrame) -> pd.DataFrame:
    display_df = station_stats.copy()
    if "station" in display_df.columns:
        display_df["station"] = display_df["station"].map(_display_station_name).fillna(display_df["station"])
    display_df = display_df.rename(columns={column: _translate_station_stat_column(column) for column in display_df.columns})
    return display_df


def _empty_figure(message: str):
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("#f6fbff")
    ax.set_facecolor("#f6fbff")
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12, color="#0f4c5c")
    ax.set_axis_off()
    fig.tight_layout()
    return fig


def _filter_by_station(df: pd.DataFrame, station: str) -> pd.DataFrame:
    internal_station = normalize_station(station)
    if internal_station and internal_station != "All Stations":
        return df[df["station"] == internal_station].copy()
    return df.copy()


def create_chart(df: pd.DataFrame, column: str, station: str, chart_type: str):
    internal_column = normalize_column(column)
    internal_station = normalize_station(station)
    internal_chart_type = normalize_chart_type(chart_type)
    display_column = _display_column_name(internal_column)

    if internal_column not in df.columns:
        return _empty_figure(f"找不到欄位：{column}")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor("#f6fbff")
    ax.set_facecolor("#f8fdff")
    plot_df = _filter_by_station(df, internal_station)

    if plot_df.empty:
        return _empty_figure("所選測站沒有可分析的資料。")

    if internal_chart_type == "Trend Line Chart":
        if internal_station == "All Stations":
            for station_name, station_df in plot_df.groupby("station"):
                station_df = station_df.sort_values("date")
                ax.plot(
                    station_df["date"],
                    station_df[internal_column],
                    marker="o",
                    linewidth=2,
                    label=_display_station_name(station_name),
                )
            ax.legend(loc="best", fontsize=8)
            title_station = "全部測站"
        else:
            plot_df = plot_df.sort_values("date")
            ax.plot(
                plot_df["date"],
                plot_df[internal_column],
                marker="o",
                linewidth=2.4,
                color="#0077b6",
                label=_display_station_name(internal_station),
            )
            ax.legend(loc="best")
            title_station = _display_station_name(internal_station)
        ax.set_title(f"{title_station} {display_column}趨勢")
        ax.set_xlabel("日期")
        ax.set_ylabel(display_column)

    elif internal_chart_type == "Station Average Bar Chart":
        bar_df = plot_df.groupby("station", as_index=False)[internal_column].mean().sort_values(internal_column)
        bar_df["station"] = bar_df["station"].map(_display_station_name).fillna(bar_df["station"])
        ax.bar(bar_df["station"], bar_df[internal_column], color="#00a6a6", edgecolor="#0077b6")
        ax.set_title(f"各測站平均{display_column}")
        ax.set_xlabel("測站")
        ax.set_ylabel(f"平均{display_column}")

    elif internal_chart_type == "Monthly Average Line Chart":
        monthly = get_monthly_average(plot_df, internal_column)
        avg_column = f"avg_{internal_column}"
        ax.plot(monthly["month"], monthly[avg_column], marker="o", linewidth=2.4, color="#0081a7")
        ax.set_title(f"月份平均{display_column}")
        ax.set_xlabel("月份")
        ax.set_ylabel(f"平均{display_column}")

    else:
        return _empty_figure("不支援的圖表類型。")

    ax.grid(True, alpha=0.25, color="#8ecae6")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    return fig


def update_dashboard(data_source: str, uploaded_file, column: str, station: str, chart_type: str):
    try:
        internal_data_source = normalize_data_source(data_source)
        internal_column = normalize_column(column)
        internal_station = normalize_station(station)
        internal_chart_type = normalize_chart_type(chart_type)

        if internal_data_source == "Upload CSV":
            if uploaded_file is None:
                raise ValueError("你選擇了上傳 CSV，但尚未選擇檔案。請上傳 CSV 或改用範例資料。")
            raw_df = load_uploaded_data(uploaded_file)
        else:
            raw_df = load_sample_data()

        cleaned_df = clean_ocean_data(raw_df)
        save_cleaned_data(cleaned_df)

        if internal_column not in NUMERIC_COLUMNS:
            supported = "、".join(COLUMN_DISPLAY_NAMES[column_name] for column_name in NUMERIC_COLUMNS)
            raise ValueError(f"選擇的分析欄位不支援。可用欄位：{supported}")

        summary = get_summary_statistics(cleaned_df)
        station_stats = get_station_statistics(cleaned_df)
        extremes = get_extreme_values(cleaned_df, internal_column)
        chart = create_chart(cleaned_df, internal_column, internal_station, internal_chart_type)

        max_row = extremes.loc[extremes["type"] == "Maximum"].iloc[0]
        min_row = extremes.loc[extremes["type"] == "Minimum"].iloc[0]
        display_column = _display_column_name(internal_column)
        message = (
            f"資料載入成功。原始資料 {len(raw_df)} 筆，清洗後資料 {len(cleaned_df)} 筆。"
            f"{display_column}最高值為 {max_row[internal_column]}（{_display_station_name(max_row['station'])}，{max_row['date']}），"
            f"最低值為 {min_row[internal_column]}（{_display_station_name(min_row['station'])}，{min_row['date']}）。"
        )

        return (
            _prepare_display_dataframe(raw_df.head(10)),
            _prepare_display_dataframe(cleaned_df.head(10)),
            _prepare_summary_display(summary),
            _prepare_station_stats_display(station_stats),
            chart,
            chart,
            message,
        )

    except Exception as exc:
        empty = pd.DataFrame()
        return (
            empty,
            empty,
            empty,
            empty,
            _empty_figure("儀表板更新失敗"),
            _empty_figure("儀表板更新失敗"),
            f"錯誤：{exc}",
        )


def build_app() -> gr.Blocks:
    with gr.Blocks(title="海洋環境資料儀表板") as demo:
        gr.Markdown(
            """
            <div class="ocean-hero">
              <h1>海洋環境資料儀表板</h1>
              <p>以 Python、Pandas、NumPy、Matplotlib 與 Gradio 建立互動式海洋資料分析介面。</p>
            </div>
            """
        )
        gr.Markdown(
            "選擇資料來源、分析欄位、測站與圖表類型後，即可查看資料預覽、清洗結果、統計摘要與視覺化圖表。",
            elem_classes=["ocean-note"],
        )

        with gr.Row():
            data_source = gr.Radio(
                DATA_SOURCE_CHOICES,
                value="範例資料",
                label="資料來源",
            )
            uploaded_file = gr.File(label="上傳 CSV 檔案", file_types=[".csv"])

        with gr.Row():
            column = gr.Dropdown(COLUMN_LABELS.keys(), value="海溫（°C）", label="分析欄位")
            station = gr.Dropdown(STATION_CHOICES, value="全部測站", label="測站")
            chart_type = gr.Dropdown(CHART_CHOICES, value="趨勢折線圖", label="圖表類型")

        update_button = gr.Button("分析 / 更新儀表板", variant="primary")
        status = gr.Textbox(label="系統狀態", interactive=False)
        main_chart_output = gr.Plot(label="主要圖表")

        with gr.Tab("原始資料預覽"):
            raw_preview = gr.Dataframe(label="原始資料前 10 筆", interactive=False)
        with gr.Tab("清洗後資料"):
            cleaned_preview = gr.Dataframe(label="清洗後資料前 10 筆", interactive=False)
        with gr.Tab("統計摘要"):
            summary_table = gr.Dataframe(label="整體統計摘要", interactive=False)
            station_table = gr.Dataframe(label="依測站分組統計", interactive=False)
        with gr.Tab("視覺化圖表"):
            chart_output = gr.Plot(label="海洋環境資料圖表")

        update_button.click(
            fn=update_dashboard,
            inputs=[data_source, uploaded_file, column, station, chart_type],
            outputs=[
                raw_preview,
                cleaned_preview,
                summary_table,
                station_table,
                chart_output,
                main_chart_output,
                status,
            ],
        )

        demo.load(
            fn=update_dashboard,
            inputs=[data_source, uploaded_file, column, station, chart_type],
            outputs=[
                raw_preview,
                cleaned_preview,
                summary_table,
                station_table,
                chart_output,
                main_chart_output,
                status,
            ],
        )

    return demo


demo = build_app()


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        theme=OCEAN_THEME,
        css=OCEAN_CSS,
    )
