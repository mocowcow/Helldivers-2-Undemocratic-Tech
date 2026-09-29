# UI 語系

使用 `python-i18n`，預設 `zh_TW`。文案集中在 `zh_TW.json`，不需提取或編譯。

## 修改文案

保留固定 key，只修改 JSON 的值；參數使用 `%{name}`。

```json
{
  "bindings": {
    "enable": "啟用 (Scroll Lock)"
  }
}
```

```python
from localization import tr

self.enable_checkbox.setText(tr("bindings.enable"))
```

新增文字時，同時加入 JSON 項目和 `tr("section.key")` 呼叫。啟用了快取，修改 JSON 後請重啟程式。

## 切換與新增語言

Settings 的「語言」選單自動掃描 `locales/*.json`。選擇後按「儲存」，重啟程式生效；缺少譯文會回退中文。

新增語言時複製現有 JSON，保留翻譯 key 與參數名稱，翻譯值並設定 `_meta.language_name` 作為選單顯示名稱（例如 `English`）。檔名不含 `.json` 的部分是固定語系代碼；沒有名稱時顯示代碼。新增檔案後重啟即可出現在選單。Qt 內建標準按鈕不由此 JSON 管理。

## 儲存與打包

設定檔新增 `language` 欄位儲存語系代碼；舊檔缺少此欄位或已儲存的語系不存在時，使用 `zh_TW`。action、按鍵、戰備識別值及 cooldown modifier key 維持原值，使用者聊天內容不翻譯。`ui/labels.py` 只負責將既有識別值對應至翻譯 key；不要把顯示文字當成儲存值。

`messages.py` 保存錯誤 key 與參數，UI 透過 `error_text()` 顯示譯文；日誌與失敗截圖檔名仍使用預設中文。

`requirements.txt` 包含 `python-i18n`；`build.bat` 直接將 `locales/` 帶入 PyInstaller。直接使用 `.spec` 時，其 datas 也需包含 `('locales', 'locales')`。不再使用 Qt Linguist、`.ts` 或 `.qm`。
