# 海洋環境資料儀表板簡報大綱

本簡報大綱對應「114-2 巨量資料與雲端運算」期末專題，主題為「海洋環境資料儀表板」。內容以大學生期末專題發表為主，重點放在專題背景、資料處理流程、系統功能、Docker 部署與成果展示。

## 第 1 頁：封面

重點：

- 專題名稱：海洋環境資料儀表板
- 課程名稱：114-2 巨量資料與雲端運算
- 技術關鍵字：Python / Pandas / Matplotlib / Gradio / Docker
- 預留 5 位組員姓名與學號欄位

建議圖像：

- 海洋或波浪背景
- 儀表板或資料分析 icon

## 第 2 頁：報告大綱

重點：

- 背景與動機
- 系統流程與方法
- 系統成果與展示
- 結論與未來改善

建議圖像：

- 四個區塊或流程箭頭

## 第 3 頁：專題背景

重點：

- 海洋環境資料包含海溫、潮位、浪高、風速與鹽度。
- 這些資料可用於觀察不同測站與日期的變化。
- 儀表板能讓資料趨勢比原始表格更容易理解。

建議圖像：

- 海洋觀測、港口或浮標示意圖

## 第 4 頁：專題動機

重點：

- 原始 CSV 不容易直接看出趨勢。
- 資料可能需要清洗、轉換與整理。
- 透過互動式儀表板可以更方便展示分析結果。

建議圖像：

- 原始資料到儀表板的轉換流程圖

## 第 5 頁：專題目的

重點：

- 建立資料清洗流程。
- 建立統計分析與視覺化功能。
- 建立可操作的 Gradio 介面。
- 使用 Docker 完成部署。

建議圖像：

- 四個卡片式區塊，分別放資料、分析、介面、部署 icon

## 第 6 頁：系統架構

重點：

- CSV 資料來源
- Python 資料讀取與清洗
- 統計分析與圖表產生
- Gradio 儀表板
- Docker 容器化部署

建議圖像：

- 橫向流程圖：CSV → 清洗 → 分析 → 視覺化 → Gradio → Docker

## 第 7 頁：資料來源與欄位

重點：

- 使用 `data/raw/sample_ocean_data.csv`。
- 資料共有 75 筆、7 個欄位。
- 測站包含 Keelung、Taichung、Kaohsiung、Hualien、Taitung。
- 欄位包含 date、station、sea_temperature_c、tide_level_m、wave_height_m、wind_speed_mps、salinity_psu。

建議圖像：

- CSV 表格截圖或欄位說明表

## 第 8 頁：資料清洗流程

重點：

- 日期欄位轉換成 datetime。
- 數值欄位轉換成 numeric。
- 缺失值使用平均值或 Unknown 處理。
- 移除重複資料並排序。
- 輸出清洗後 CSV。

建議圖像：

- 原始資料 → 清洗規則 → 清洗後資料流程圖

## 第 9 頁：資料分析方法

重點：

- 整體統計摘要。
- 測站分組統計。
- 月份平均分析。
- 最大值與最小值分析。

建議圖像：

- 四格分析方法卡片

## 第 10 頁：視覺化結果

重點：

- Trend Line Chart 顯示時間趨勢。
- Station Average Bar Chart 比較測站平均值。
- Monthly Average Line Chart 顯示月份平均變化。

建議圖像：

- 放入 Matplotlib 圖表截圖

## 第 11 頁：Gradio 介面與 Docker 部署

重點：

- Gradio 可選擇資料來源、欄位、測站與圖表類型。
- Docker build 指令：`docker build -t ocean-data-dashboard -f docker/Dockerfile .`
- Docker run 指令：`docker run -p 7860:7860 ocean-data-dashboard`
- 啟動後開啟 `http://localhost:7860`

建議圖像：

- Gradio 系統截圖
- Docker icon 或部署流程

## 第 12 頁：結論與未來改善

重點：

- 完成資料讀取、清洗、分析與視覺化。
- 完成 Gradio 互動式儀表板。
- 完成 Docker 容器化部署。
- 未來可串接真實海洋觀測 API、加入地圖與異常警示。

建議圖像：

- 成果與未來改善雙欄版面
