const fs = require('fs');
const path = require('path');
const PptxGenJS = require('pptxgenjs');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'Ocean_Environment_Dashboard_Final_Presentation.pptx');
const img = (...p) => path.join(ROOT, ...p);

function read(rel) { return fs.readFileSync(path.join(ROOT, rel), 'utf8'); }
function csvRows() {
  const raw = read('data/raw/sample_ocean_data.csv').trim().split(/\r?\n/);
  const headers = raw[0].split(',');
  const rows = raw.slice(1).map(line => {
    const values = line.split(',');
    return Object.fromEntries(headers.map((h, i) => [h, values[i]]));
  });
  return { headers, rows };
}

const project = {
  readme: read('README.md'),
  dataReadme: read('data/README.md'),
  report: read('docs/report.md'),
  cleanCode: read('src/analysis/clean_data.py'),
  analyzeCode: read('src/analysis/analyze_data.py'),
  appCode: read('src/app/gradio_app.py'),
  dockerfile: read('docker/Dockerfile'),
};
const { headers, rows } = csvRows();
const stations = [...new Set(rows.map(r => r.station))];
const stationZh = { Keelung: '基隆', Taichung: '台中', Kaohsiung: '高雄', Hualien: '花蓮', Taitung: '台東' };
const fieldUnits = [
  ['date', '日期', '年-月-日'],
  ['station', '測站名稱', '無'],
  ['sea_temperature_c', '海溫', '°C'],
  ['tide_level_m', '潮位', '公尺'],
  ['wave_height_m', '浪高', '公尺'],
  ['wind_speed_mps', '風速', 'm/s'],
  ['salinity_psu', '鹽度', 'PSU'],
];

const actualFacts = {
  hasUpload: project.appCode.includes('上傳 CSV') || project.appCode.includes('Upload CSV'),
  hasMainChart: project.appCode.includes('主要圖表'),
  hasDockerPort: project.dockerfile.includes('7860'),
  hasNoto: project.dockerfile.includes('fonts-noto-cjk'),
  cleanRules: [
    project.cleanCode.includes('pd.to_datetime') ? 'date 轉成 datetime，無效日期移除' : null,
    project.cleanCode.includes('pd.to_numeric') ? '海溫、潮位、浪高、風速、鹽度轉 numeric' : null,
    project.cleanCode.includes('fillna') && project.cleanCode.includes('mean') ? '數值缺失值以欄位平均值補值' : null,
    project.cleanCode.includes('Unknown') ? '測站缺失值標記為 Unknown' : null,
    project.cleanCode.includes('drop_duplicates') ? '移除重複資料並輸出 cleaned CSV' : null,
  ].filter(Boolean),
  analysis: [
    project.analyzeCode.includes('describe') ? '整體統計摘要' : null,
    project.analyzeCode.includes('groupby("station")') ? '依測站分組統計' : null,
    project.analyzeCode.includes('to_period("M")') ? '月份平均分析' : null,
    project.analyzeCode.includes('idxmax') && project.analyzeCode.includes('idxmin') ? '最大值與最小值查詢' : null,
  ].filter(Boolean),
};

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Codex';
pptx.subject = '114-2 巨量資料與雲端運算期末專題';
pptx.title = '海洋環境資料儀表板';
pptx.company = 'MiniMax pptx-generator workflow';
pptx.lang = 'zh-TW';
pptx.theme = {
  headFontFace: 'Microsoft YaHei',
  bodyFontFace: 'Microsoft YaHei',
  lang: 'zh-TW',
};
pptx.defineLayout({ name: 'CUSTOM_WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'CUSTOM_WIDE';

const C = {
  navy: '073B4C', blue: '0077B6', cyan: '00B4D8', aqua: '90E0EF', pale: 'EAF8FB',
  white: 'FFFFFF', gray: 'EEF2F5', text: '12313F', muted: '5A6B75', green: '2A9D8F', orange: 'F4A261', line: 'CDEAF2'
};

function addText(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: opts.fontFace || 'Microsoft YaHei',
    fontSize: opts.fontSize || 16,
    color: opts.color || C.text,
    bold: opts.bold || false,
    align: opts.align || 'left',
    valign: opts.valign || 'top',
    margin: opts.margin ?? 0.03,
    breakLine: false,
    fit: 'shrink',
  });
}
function title(slide, t, sub, n) {
  addText(slide, t, 0.55, 0.35, 8.4, 0.45, { fontSize: 28, bold: true, color: C.navy });
  slide.addShape(pptx.ShapeType.rect, { x: 0.55, y: 0.95, w: 1.2, h: 0.055, fill: { color: C.cyan }, line: { color: C.cyan } });
  if (sub) addText(slide, sub, 0.58, 1.12, 9.2, 0.28, { fontSize: 13, color: C.muted });
  if (n) badge(slide, String(n), 12.35, 6.85, 0.45, C.blue);
}
function badge(slide, text, x, y, w = 0.78, color = C.blue) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h: 0.36, rectRadius: 0.08, fill: { color }, line: { color } });
  addText(slide, text, x, y + 0.08, w, 0.16, { fontSize: 9.5, bold: true, color: C.white, align: 'center' });
}
function card(slide, x, y, w, h, heading, body, color = C.cyan) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: C.white }, line: { color: C.aqua, width: 1 } });
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.08, h, fill: { color }, line: { color } });
  addText(slide, heading, x + 0.2, y + 0.15, w - 0.35, 0.28, { fontSize: 16, bold: true, color: C.navy });
  addText(slide, body, x + 0.2, y + 0.56, w - 0.35, h - 0.65, { fontSize: 12.4, color: C.text, breakLine: true });
}
function bullets(slide, items, x, y, w, gap = 0.46, size = 15) {
  items.slice(0, 5).forEach((it, i) => {
    slide.addShape(pptx.ShapeType.ellipse, { x, y: y + i * gap + 0.12, w: 0.12, h: 0.12, fill: { color: C.cyan }, line: { color: C.cyan } });
    addText(slide, it, x + 0.25, y + i * gap, w - 0.25, 0.34, { fontSize: size, color: C.text });
  });
}
function image(slide, file, x, y, w, h) {
  if (fs.existsSync(file)) slide.addImage({ path: file, x, y, w, h, sizing: { type: 'contain', x, y, w, h } });
  else {
    slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, fill: { color: C.gray }, line: { color: C.line } });
    addText(slide, '截圖 / 圖表預留區', x, y + h / 2 - 0.12, w, 0.25, { align: 'center', fontSize: 14, color: C.muted });
  }
}
function connector(slide, x, y) {
  slide.addShape(pptx.ShapeType.rightArrow, { x, y, w: 0.38, h: 0.22, fill: { color: C.blue }, line: { color: C.blue } });
}
function bg(slide, color = C.white) { slide.background = { color }; }

// 1
let s = pptx.addSlide(); bg(s, C.navy);
s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 7.5, fill: { color: C.navy }, line: { color: C.navy } });
['0077B6', '00B4D8', '90E0EF'].forEach((color, i) => {
  s.addShape(pptx.ShapeType.arc, { x: -0.4 + i * 1.7, y: 6.15 - i * 0.15, w: 5.4, h: 1.25, adjustPoint: 0.35, fill: { color }, line: { color } });
});
addText(s, '海洋環境資料儀表板', 1.0, 2.18, 11.3, 0.65, { fontSize: 36, bold: true, color: C.white, align: 'center' });
addText(s, '114-2 巨量資料與雲端運算', 2.65, 3.05, 8.0, 0.38, { fontSize: 20, color: C.aqua, align: 'center' });
addText(s, 'Python / Pandas / Matplotlib / Gradio / Docker', 2.55, 4.03, 8.2, 0.32, { fontSize: 14, color: C.white, align: 'center' });
badge(s, '小組專題', 5.95, 3.58, 1.4, C.green);
addText(
  s,
  '組員 1：________  學號：________    組員 2：________  學號：________\n組員 3：________  學號：________    組員 4：________  學號：________\n組員 5：________  學號：________',
  2.3,
  4.55,
  8.8,
  0.58,
  { fontSize: 8.5, color: C.white, align: 'center' }
);

// 2
s = pptx.addSlide(); bg(s, C.pale); title(s, '報告大綱', '以四個部分說明本次期末專題', 2);
[['01','背景與動機','專題背景、動機與目的'],['02','系統流程與方法','系統架構、資料處理、使用技術'],['03','系統成果與展示','資料視覺化、Gradio 介面、Docker 部署'],['04','結論與未來改善','完成成果與後續方向']].forEach((a,i)=>card(s, 0.85+(i%2)*5.8, 1.75+Math.floor(i/2)*1.7, 5.0, 1.15, `${a[0]}  ${a[1]}`, a[2], [C.blue,C.green,C.cyan,C.orange][i]));

// 3
s = pptx.addSlide(); bg(s); title(s, '專題背景', '依據 README、proposal 與 report 整理', 3);
bullets(s, ['海洋環境資料包含海溫、潮位、浪高、風速與鹽度。','資料可反映不同測站與日期之間的環境變化。','原始觀測資料通常需要整理後才容易理解。','以儀表板呈現，可快速查看趨勢、統計與圖表。'], 0.8, 1.75, 5.8, 0.55, 16);
s.addShape(pptx.ShapeType.roundRect, {x:7.25,y:1.55,w:4.8,h:3.3,rectRadius:0.08,fill:{color:C.pale},line:{color:C.aqua}});
addText(s, '海洋資料儀表板示意', 7.55, 1.85, 4.2, 0.35, {fontSize:18,bold:true,color:C.navy,align:'center'});
addText(s, `Sample rows: ${rows.length}\nStations: ${stations.map(v=>stationZh[v]||v).join('、')}\nFields: ${headers.length}`, 7.95, 2.55, 3.3, 1.1, {fontSize:16,color:C.text,align:'center'});

// 4
s = pptx.addSlide(); bg(s, C.pale); title(s, '專題動機', '將原始資料轉換為可互動分析的系統', 4);
card(s,0.7,1.72,3.15,1.25,'原始資料','CSV 或表格格式不容易直接看出趨勢。',C.blue);
connector(s,4.1,2.18);
card(s,4.65,1.72,3.15,1.25,'分析處理','資料清洗、統計摘要與分組分析。',C.green);
connector(s,8.05,2.18);
card(s,8.6,1.72,3.15,1.25,'儀表板','透過 Gradio 互動選欄位、測站與圖表。',C.cyan);
addText(s, '重點：建立可互動分析、可視覺化呈現、可 Docker 部署的資料應用系統。', 1.2, 4.45, 10.9, 0.45, {fontSize:18,bold:true,color:C.navy,align:'center'});

// 5
s = pptx.addSlide(); bg(s); title(s, '專題目的', '依據專案已完成功能整理', 5);
[['資料處理','讀取 sample CSV 或上傳 CSV，並進行清洗。',C.blue],['統計分析','產生整體摘要、測站分組、月份平均與極值。',C.green],['視覺化展示','用 Matplotlib 產生趨勢折線圖與長條圖。',C.cyan],['部署展示','以 Gradio 提供介面，Docker 容器化部署。',C.orange]].forEach((a,i)=>card(s,0.65+(i%2)*6.05,1.55+Math.floor(i/2)*1.55,5.35,1.1,a[0],a[1],a[2]));

// 6
s = pptx.addSlide(); bg(s, C.pale); title(s, '系統架構', '根據 src/ 與 docker/ 實際檔案整理', 6);
['資料來源','資料讀取','資料清洗','統計分析','圖表產生','Gradio 介面','Docker 部署'].forEach((stage,i)=>{
  const x=0.4+i*1.72;
  s.addShape(pptx.ShapeType.roundRect,{x,y:2.35,w:1.28,h:0.7,rectRadius:0.06,fill:{color:C.white},line:{color:C.cyan}});
  addText(s,stage,x+0.05,2.58,1.18,0.16,{fontSize:10.5,bold:true,color:C.navy,align:'center'});
  if(i<6) connector(s,x+1.35,2.58);
});
['data/raw','data_loader.py','clean_data.py','analyze_data.py','Matplotlib','gradio_app.py','Dockerfile'].forEach((txt,i)=>addText(s,txt,0.4+i*1.72,3.22,1.28,0.25,{fontSize:8.5,color:C.muted,align:'center',fontFace:'Arial'}));

// 7
s = pptx.addSlide(); bg(s); title(s, '資料來源與欄位', `實際資料：data/raw/sample_ocean_data.csv，共 ${rows.length} 筆`, 7);
fieldUnits.forEach((f,i)=>{ addText(s,f[0],0.85,1.45+i*0.42,2.45,0.22,{fontSize:11.5,bold:true,color:C.navy,fontFace:'Arial'}); addText(s,`${f[1]} / ${f[2]}`,3.35,1.45+i*0.42,2.2,0.22,{fontSize:11.5,color:C.text}); });
image(s,img('docs','presentation_assets','sample_data_table.png'),6.1,1.45,5.75,2.2);
addText(s, `測站：${stations.map(v=>stationZh[v]||v).join('、')}`, 0.9, 5.35, 11.2, 0.26, {fontSize:15,color:C.muted,align:'center'});

// 8
s = pptx.addSlide(); bg(s, C.pale); title(s, '資料清洗流程', '根據 src/analysis/clean_data.py 的實際邏輯', 8);
card(s,0.7,1.55,2.8,1.0,'原始資料','sample CSV / 使用者上傳 CSV',C.blue); connector(s,3.75,1.9); card(s,4.35,1.55,2.8,1.0,'清洗規則','日期、數值、缺失值、重複資料',C.green); connector(s,7.4,1.9); card(s,8.0,1.55,3.0,1.0,'清洗後資料','data/processed/cleaned_ocean_data.csv',C.cyan);
bullets(s, actualFacts.cleanRules, 1.0, 3.25, 10.8, 0.42, 14.2);

// 9
s = pptx.addSlide(); bg(s); title(s, '資料分析方法', '根據 src/analysis/analyze_data.py 的實際功能', 9);
actualFacts.analysis.forEach((name,i)=>card(s,0.75+(i%2)*5.95,1.65+Math.floor(i/2)*1.45,5.2,1.05,name,['使用 describe 與 NumPy 補充全距、變異數。','比較不同測站的平均值、最小值、最大值。','以月份彙整指定欄位平均值。','找出指定欄位最大與最小紀錄。'][i]||'', [C.blue,C.green,C.cyan,C.orange][i]));

// 10
s = pptx.addSlide(); bg(s, C.pale); title(s, '視覺化結果', '根據 Matplotlib 與目前專案資料產生', 10);
image(s,img('docs','presentation_assets','sea_temperature_trend.png'),0.55,1.35,5.75,2.55);
image(s,img('docs','presentation_assets','station_average_temperature.png'),6.75,1.35,5.4,2.55);
addText(s,'重點觀察：圖表能快速比較不同測站與日期的海溫、浪高等變化。',1.2,5.05,10.8,0.3,{fontSize:16,bold:true,color:C.navy,align:'center'});

// 11
s = pptx.addSlide(); bg(s); title(s, 'Gradio 介面與 Docker 部署', '根據 src/app/gradio_app.py 與 docker/Dockerfile 整理', 11);
image(s,img('docs','screenshots','ocean_dashboard_home.png'),0.55,1.35,6.15,3.75);
card(s,7.1,1.35,4.9,1.5,'Gradio 介面功能','使用範例資料 / 上傳 CSV\n選擇分析欄位、測站、圖表類型\n顯示資料預覽、統計摘要與主要圖表',C.cyan);
s.addShape(pptx.ShapeType.roundRect,{x:7.1,y:3.3,w:4.9,h:1.35,rectRadius:0.08,fill:{color:C.gray},line:{color:C.aqua}});
addText(s,'docker build -t ocean-data-dashboard -f docker/Dockerfile .\ndocker run -p 7860:7860 ocean-data-dashboard\nhttp://localhost:7860',7.28,3.55,4.55,0.65,{fontSize:10.5,color:C.text,fontFace:'Arial'});
badge(s,actualFacts.hasNoto?'Noto CJK 字型':'Docker',8.85,5.12,1.5,C.blue);

// 12
s = pptx.addSlide(); bg(s, C.pale); title(s, '結論與未來改善', '根據 README 與 docs/report.md 整理', 12);
card(s,0.75,1.45,5.45,2.5,'專題成果','完成資料讀取與清洗流程。\n完成統計分析與視覺化功能。\n建立 Gradio 互動式儀表板。\n完成 Docker 容器化部署。',C.blue);
card(s,6.85,1.45,5.45,2.5,'未來改善','串接真實海洋觀測 API。\n加入即時資料更新功能。\n增加浪高或風速異常警示。\n加入地圖視覺化顯示測站位置。',C.green);
s.addShape(pptx.ShapeType.roundRect,{x:1.25,y:5.25,w:10.85,h:0.5,rectRadius:0.08,fill:{color:C.navy},line:{color:C.navy}});
addText(s,'本專題完成從資料處理、分析視覺化到 Docker 部署的完整流程。',1.4,5.39,10.55,0.18,{fontSize:16,bold:true,color:C.white,align:'center'});

pptx.writeFile({ fileName: OUT }).then(() => console.log(`created=${OUT}`));
