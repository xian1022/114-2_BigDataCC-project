# 海洋環境資料儀表板期末報告

## 專題資訊

| 項目 | 內容 |
| --- | --- |
| 課程 | 114-2 巨量資料與雲端運算 |
| 專題名稱 | 海洋環境資料儀表板 |
| 專題形式 | 小組專題 |
| 使用技術 | Python、Pandas、NumPy、Matplotlib、Gradio、Docker |
| Demo 網址 | `http://localhost:7860` |

## 組員資訊

| 序號 | 姓名 | 學號 |
| --- | --- | --- |
| 組員 1 |  |  |
| 組員 2 |  |  |
| 組員 3 |  |  |
| 組員 4 |  |  |
| 組員 5 |  |  |

## 摘要

本專題建立一個「海洋環境資料儀表板」，使用 Python 對海洋環境資料進行清洗、統計分析與視覺化，並使用 Gradio 建立互動式網頁介面。系統支援內建 sample CSV 與使用者上傳 CSV，能顯示原始資料預覽、清洗後資料、整體統計摘要、測站分組統計與 Matplotlib 圖表。最後透過 Docker 容器化，讓使用者可以用一致的方式啟動系統。

## 一、專題動機與目標

海洋環境資料包含日期、測站、海溫、潮位、浪高、風速與鹽度等資訊，很適合用來練習資料清洗、分組分析與視覺化。若只使用原始表格，很難快速看出不同測站之間的差異與時間變化。本專題希望將資料分析流程做成可以操作的 Web 儀表板，讓使用者透過瀏覽器即可完成資料預覽、分析與圖表產生。

本專題的主要目標如下：

- 建立可重現的海洋環境資料分析流程。
- 使用 Pandas 與 NumPy 完成資料清洗與統計分析。
- 使用 Matplotlib 產生清楚的視覺化圖表。
- 使用 Gradio 建立互動式儀表板。
- 使用 Docker 完成容器化部署。

## 二、資料集說明

本專題使用 `data/raw/sample_ocean_data.csv` 作為範例資料。此資料為期末專題展示用自建模擬資料，並不是從真實測站直接下載。資料格式參考海洋觀測資料常見欄位設計，主要用於展示資料清洗、統計分析與視覺化流程。

| 項目 | 內容 |
| --- | --- |
| 檔案名稱 | `sample_ocean_data.csv` |
| 資料位置 | `data/raw/sample_ocean_data.csv` |
| 資料量 | 75 筆 |
| 日期範圍 | 2026-03-01 至 2026-03-15 |
| 測站 | Keelung、Taichung、Kaohsiung、Hualien、Taitung |
| 欄位數 | 7 個 |

若要改用真實資料，建議使用交通部中央氣象署開放資料平臺。可先申請 API 授權碼，再查詢海象監測資料，例如 `O-B0075-001` 48 小時浮標站與潮位站海況監測資料。該類資料可提供潮高、浪高、海溫、風速等欄位，整理後可轉換成本專案所需格式。若資料來源沒有鹽度欄位，需另外尋找鹽度資料來源，或修改系統讓鹽度欄位變成選填。

| 欄位名稱 | 說明 | 單位 |
| --- | --- | --- |
| `date` | 觀測日期 | 年-月-日 |
| `station` | 測站名稱 | 無 |
| `sea_temperature_c` | 海溫 | 攝氏度 |
| `tide_level_m` | 潮位 | 公尺 |
| `wave_height_m` | 浪高 | 公尺 |
| `wind_speed_mps` | 風速 | m/s |
| `salinity_psu` | 鹽度 | PSU |

## 三、技術架構

系統主要分成六個部分：資料讀取、資料清洗、統計分析、視覺化、Gradio 互動介面與 Docker 部署。

```text
CSV 資料
→ data_loader.py
→ clean_data.py
→ analyze_data.py
→ Matplotlib 圖表
→ Gradio 儀表板
→ Docker 部署
```

各模組說明如下：

| 模組 | 說明 |
| --- | --- |
| `src/utils/data_loader.py` | 讀取 sample CSV 或使用者上傳 CSV |
| `src/analysis/clean_data.py` | 清洗資料、轉換欄位、補缺失值、輸出清洗後資料 |
| `src/analysis/analyze_data.py` | 產生統計摘要、測站統計、月份平均與極值 |
| `src/app/gradio_app.py` | 建立互動式儀表板並顯示資料與圖表 |
| `docker/Dockerfile` | 建立可部署的 Docker 容器 |

## 四、資料分析過程

### 4.1 資料清洗

資料清洗流程首先確認 CSV 是否包含必要欄位。接著將 `date` 欄位轉換為 datetime 格式，若日期無法轉換則移除該筆資料。數值欄位會轉換為 numeric，如果出現缺失值，則使用該欄位平均值補值。`station` 欄位若缺失會填入 `Unknown`。最後系統會移除重複資料，並依照日期與測站排序，將清洗後結果輸出至 `data/processed/cleaned_ocean_data.csv`。

### 4.2 統計分析

統計分析包含整體描述統計、依測站分組統計、月份平均值與最大最小值查詢。整體描述統計使用平均值、標準差、最小值、四分位數與最大值來觀察資料分布。測站分組統計則比較不同測站在各欄位的平均值、最小值與最大值。月份平均值可用於觀察時間尺度上的變化趨勢，極值查詢則可找出特定欄位的最高與最低紀錄。

### 4.3 視覺化

本專題使用 Matplotlib 製作圖表，包含趨勢折線圖、測站平均長條圖與月份平均折線圖。折線圖適合觀察不同日期的變化，長條圖適合比較不同測站的平均差異，月份平均折線圖則適合觀察較粗略的時間趨勢。為了避免 Docker 環境中文字型問題，圖表標題與座標軸主要使用英文。

## 五、應用程式功能

本專題未使用機器學習模型，而是將重點放在資料分析與互動式儀表板。Gradio 介面提供以下功能：

- 選擇使用 sample data 或上傳 CSV。
- 選擇分析欄位。
- 選擇全部測站或單一測站。
- 選擇圖表類型。
- 顯示原始資料前 10 列。
- 顯示清洗後資料前 10 列。
- 顯示整體統計摘要與測站統計。
- 顯示 Matplotlib 視覺化圖表。

## 六、Docker 部署

本專題提供 Dockerfile，使用 Python 3.11 slim 映像檔，安裝 requirements 後複製專案檔案，並以 `python -m src.app.gradio_app` 啟動 Gradio App。Dockerfile 也安裝 `fontconfig` 與 `fonts-noto-cjk`，讓容器內的中文字型顯示更穩定。

Docker build 指令：

```bash
docker build -t ocean-data-dashboard -f docker/Dockerfile .
```

Docker run 指令：

```bash
docker run -p 7860:7860 ocean-data-dashboard
```

啟動後開啟：

```text
http://localhost:7860
```

## 七、成果展示

系統啟動後，使用者會看到「海洋環境資料儀表板」頁面。介面上方提供資料來源、分析欄位、測站與圖表類型選項；按下分析按鈕後，系統會顯示資料表、統計結果與圖表。

系統截圖存放於：

```text
docs/screenshots/ocean_dashboard_home.png
```

![海洋環境資料儀表板截圖](screenshots/ocean_dashboard_home.png)

## 八、結果討論

從 sample 資料可以看到不同測站在海溫、浪高與潮位等欄位上有不同平均水準。以圖表呈現後，測站之間的差異比單純閱讀表格更明顯。此系統雖然使用模擬資料，但已經能展示完整的資料分析流程，也能支援使用者上傳符合格式的資料進行相同分析。

系統目前適合用於課堂 Demo 與資料分析流程展示。若要應用於真實場景，後續需要串接真實資料來源，並加入資料更新、異常值偵測與更多視覺化方式。

## 九、心得與建議

透過本專題，可以練習從資料檔案開始，逐步完成資料清洗、統計分析、視覺化、互動介面與 Docker 部署。過程中也能理解，資料分析專案不只需要寫出分析程式，也需要考慮使用者如何操作、系統如何啟動，以及不同環境下是否能穩定重現。

未來若繼續改進，可以加入真實海洋觀測 API、地圖視覺化、異常值警示、資料下載功能與更多互動篩選條件，讓儀表板更接近實際應用。

## 十、參考資料

- Python 官方文件：https://docs.python.org/
- Pandas 官方文件：https://pandas.pydata.org/docs/
- NumPy 官方文件：https://numpy.org/doc/
- Matplotlib 官方文件：https://matplotlib.org/stable/
- Gradio 官方文件：https://www.gradio.app/docs
- Docker 官方文件：https://docs.docker.com/
- 中央氣象署開放資料平臺：https://opendata.cwa.gov.tw/
- 中央氣象署 API 線上說明文件：https://opendata.cwa.gov.tw/dist/opendata-swagger.html
- 海象監測資料 O-B0075-001：https://opendata.cwa.gov.tw/dataset/observation/O-B0075-001
- 海象觀測測站資料 O-B0076-001：https://opendata.cwa.gov.tw/dataset/forecast/O-B0076-001
- ASRAD 海象站海溫資料 CSV：https://asrad.pccu.edu.tw/dbar/digital_data/4-1-%E6%B5%B7%E6%BA%ABcsv/
