# Terminal 方向辨識模組

由主程式 Settings 設定「Terminal 辨識快捷鍵」，勾選「啟用」後生效；「儲存」才寫入設定檔。

## 執行流程

擷取主螢幕完整畫面，自動定位箭頭列，以灰階輪廓及模板辨識方向。成功後依序輸入 W/A/S/D；不按 Ctrl 或 Enter。遊戲須保持前景，目前沒有前景檢查。

高度超過 720 像素的截圖先縮圖定位 ROI，再以原圖像素辨識方向；若定位或辨識失敗，改以原尺寸重試。debug 輸出分別保存在 `coarse/`、`full/`，各層的最終 ROI 使用原圖座標。備援視角校正最多使用兩個工作執行緒，仍要求成功結果彼此一致。

從熱鍵請求開始計算 2 秒時限，包含截圖與排程等待。超時或一般失敗均顯示 popup 並記錄 log，超時結果不再觸發按鍵。原生呼叫會在返回後中止，GUI 忙碌時 popup 可能稍晚顯示；已開始的送鍵時間不計入辨識時限。

失敗時保存當次原始截圖至 `SETTINGS_PATH.parent / "failed"`（`%LOCALAPPDATA%/HD2/failed`），檔名為「失敗原因_時間戳.png」。若沒有取得截圖，則無圖片可保存。

## 保留的檔案

| 檔案 | 用途 |
| --- | --- |
| `capture.py` | Qt 截圖、背景辨識、送鍵、失敗提示與截圖保存 |
| `deadline.py` | 辨識截止時間檢查 |
| `detection.py` | 完整圖片中的箭頭列定位 |
| `terminal.py` | 輪廓分割、模板比對、可信度與完整性檢查 |
| `matching.py` | 批次計算模板正規化相關係數，共用平移搜尋的統計值 |
| `refinements.py` | 辨識流程使用的有限視角校正 |
| `templates/terminal/` | 一般箭頭模板 |
| `templates/terminal_slanted/` | 斜視角箭頭模板 |

模板是執行依賴，必須保留並隨 PyInstaller 打包；`sources.json` 保留模板來源紀錄，不需要原始樣本圖片即可執行。

核心 API `recognize_screenshot(image)` 回傳 `(方向序列, ROI)`，`recognize_directions(image, roi=...)` 辨識指定範圍。兩者接受 NumPy 圖片，核心辨識不依賴 UI 或螢幕擷取。樣本資料、手動測試 GUI/CLI、benchmark 與透視實驗入口已移除。
