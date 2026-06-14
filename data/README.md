# 資料集說明

本資料夾屬於「海洋環境資料儀表板」專題，用於存放原始範例資料與清洗後資料。

## 資料來源

| 項目 | 說明 |
| --- | --- |
| 資料名稱 | 海洋環境範例資料 |
| 原始檔案 | `data/raw/sample_ocean_data.csv` |
| 清洗後檔案 | `data/processed/cleaned_ocean_data.csv` |
| 資料格式 | CSV |
| 資料量 | 75 筆 |
| 欄位數 | 7 個欄位 |
| 日期範圍 | 2026-03-01 至 2026-03-15 |
| 測站 | Keelung、Taichung、Kaohsiung、Hualien、Taitung |
| 來源說明 | 期末專題展示用自建模擬資料 |
| 授權方式 | 專題自建資料，僅供課堂展示與程式測試使用 |

本資料為期末專題展示用之模擬資料，並非從政府開放資料或真實測站直接下載。資料格式參考海洋觀測資料常見欄位設計，主要用於展示資料清洗、統計分析與視覺化流程。

## 欄位定義

| 欄位名稱 | 資料型態 | 欄位意義 | 單位或格式 |
| --- | --- | --- | --- |
| `date` | date/string | 觀測日期 | `YYYY-MM-DD` |
| `station` | string | 測站名稱 | 無 |
| `sea_temperature_c` | float | 海水溫度 | 攝氏度 |
| `tide_level_m` | float | 潮位高度 | 公尺 |
| `wave_height_m` | float | 浪高 | 公尺 |
| `wind_speed_mps` | float | 風速 | 公尺/秒 |
| `salinity_psu` | float | 鹽度 | PSU |

## 資料夾結構

```text
data/
├── raw/
│   └── sample_ocean_data.csv
├── processed/
│   └── cleaned_ocean_data.csv
└── README.md
```

## 原始資料說明

`data/raw/sample_ocean_data.csv` 是系統預設讀取的範例資料。資料包含五個測站與多天觀測紀錄，可用於展示不同測站與不同日期之間的海洋環境變化。

目前範例資料包含以下特性：

- 每筆資料代表某一天、某一測站的一組海洋環境觀測值。
- 測站包含 Keelung、Taichung、Kaohsiung、Hualien、Taitung。
- 欄位包含海溫、潮位、浪高、風速與鹽度。
- 資料已設計基本變化趨勢，方便產生折線圖與長條圖。

## 若要改用真實資料

若要將本專題改成真實資料版本，建議使用交通部中央氣象署開放資料平臺。

建議來源：

| 資料來源 | 說明 |
| --- | --- |
| 中央氣象署開放資料平臺 | 官方氣象與海象資料入口，可申請 API 授權碼 |
| `O-B0075-001` 海象監測資料 | 48 小時浮標站與潮位站海況監測資料，包含潮高、浪高、海溫、風速等欄位 |
| `O-B0076-001` 海象觀測測站資料 | 可作為測站代碼與測站名稱對照 |
| ASRAD 海象站海溫 CSV | 可下載中央氣象署海象站海溫歷史 CSV |

基本流程：

1. 到中央氣象署開放資料平臺註冊帳號。
2. 取得 API 授權碼。
3. 在 API 線上說明文件查詢海象資料集，例如 `O-B0075-001`。
4. 使用 Python `requests` 下載 JSON 或 ZIP/CSV。
5. 使用 Pandas 整理欄位，轉換成本專案需要的欄位名稱。
6. 輸出成 `data/raw/real_ocean_data.csv`。
7. 透過 Gradio 的上傳 CSV 功能進行分析。

API URL 範例：

```text
https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-B0075-001?Authorization=你的_API_KEY&format=JSON
```

欄位轉換建議：

| 真實資料欄位 | 本專案欄位 |
| --- | --- |
| 測站代碼或測站名稱 | `station` |
| 資料觀測時間 | `date` |
| 海溫 | `sea_temperature_c` |
| 潮高或潮位 | `tide_level_m` |
| 浪高 | `wave_height_m` |
| 風速 | `wind_speed_mps` |

注意：中央氣象署不同資料集提供的欄位不完全相同，可能沒有鹽度 `salinity_psu`。若正式改用真實資料，應另外尋找鹽度資料來源，或修改程式讓鹽度欄位成為選填欄位，避免把缺少鹽度資料誤解為真實觀測值。

## 清洗後資料說明

`data/processed/cleaned_ocean_data.csv` 會在執行清洗流程或 Gradio App 後自動產生。清洗流程包含：

- 檢查必要欄位。
- 將 `date` 欄位轉為 datetime。
- 將數值欄位轉為 numeric。
- 移除無法轉換日期的資料。
- 數值欄位缺失值使用欄位平均值補齊。
- `station` 缺失值填入 `Unknown`。
- 移除重複資料。
- 依日期與測站排序。

## 注意事項

- 本資料不是實際海洋觀測資料，不應用於真實決策或正式研究。
- 使用者若上傳自己的 CSV，欄位名稱需符合本專案要求。
- `data/processed/*.csv` 已設定在 `.gitignore` 中，清洗後資料可由程式重新產生。
- 若日後改用真實公開資料，需在此文件補上來源網址、下載日期與授權方式。
