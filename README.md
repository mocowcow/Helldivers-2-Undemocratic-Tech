# HD2 Undemocratic Tech

Windows 上的 Helldivers 2 快捷鍵與聊天輔助工具，使用 PySide6、keyboard 及 pydirectinput。

## 專案結構

| 路徑 | 責任 |
| --- | --- |
| `main.py` | 建立應用程式、載入設定、串接元件與釋放快捷鍵 |
| `ui/binding_panel.py` | 分頁導航、手動啟用綁定、欄位鎖定與儲存操作 |
| `ui/binding_table.py` | 戰略配備與聊天綁定的共用表格 |
| `ui/settings_page.py` | 設定檔位置、儲存按鈕與聊天視窗快捷鍵 |
| `ui/key_input.py` | 單一按鍵擷取，Esc 清除綁定 |
| `ui/chat_input.py` | 聊天輸入視窗、輸入法狀態及送出流程 |
| `ui/stratagem_picker.py` | 分類 SVG 選擇視窗，每列 10 個項目 |
| `ui/hud_overlay.py` | 獨立控制的置頂 HUD，顯示綁定按鍵與圖示，支援拖曳 |
| `hotkeys/models.py` | 不依賴 UI 或輸入工具的 Binding 資料模型 |
| `hotkeys/manager.py` | 快捷鍵註冊、移除、替換與失敗還原 |
| `hotkeys/validation.py` | 綁定驗證及排除未綁定項目 |
| `hotkeys/keys.py` | 按鍵名稱轉換為 scan code 與數字鍵盤身分 |
| `game/actions.py` | 聊天文字與戰略配備按鍵序列輸入 |
| `game/windows.py` | 聊天視窗使用的 Win32 前景查詢與聚焦函數 |
| `config/defaults.py` | 預設綁定及輸入間隔 |
| `config/settings.py` | JSON 設定讀寫及原子替換 |
| `stratagems.py` | 戰略配備名稱、分類、指令及 SVG 檔名 |
| `resources.py` | 原始碼與 PyInstaller 封裝環境共用的資源路徑 |
| `diagnostics.py` | Console 與 UTF-8 檔案日誌，以及未處理例外紀錄 |
| `stratagems-svg/`、`icon.ico` | UI 圖示資源 |

## 啟動與打包

在專案根目錄執行：

```bat
python -m pip install -r requirements.txt
python main.py
```

打包前另行安裝 PyInstaller，再執行 `build.bat`：

```bat
python -m pip install pyinstaller
build.bat
```

目前腳本使用 `--onefile --noconsole`，包含 `icon.ico` 與 `stratagems-svg` 資源，產物為 `dist\HD2 Undemocratic Tech.exe`。打包版不開啟 console，執行紀錄仍寫入日誌檔案。

## 設定行為

1. 在 Stratagem binding 與 Chat binding 分頁設定戰略配備或預設聊天文字，點擊快捷鍵欄位後按下單一按鍵；放開確定，Esc 清除該綁定。
2. 在 Settings 設定開啟聊天輸入視窗的快捷鍵。
3. 勾選主 UI 的「啟用」後，依目前內容註冊熱鍵。所有綁定欄位與增加／刪除操作會鎖定；取消勾選後解除綁定並解鎖。
4. Settings 的「儲存」獨立保存目前設定；啟用與停用不會自動儲存。分頁切換、儲存與開啟儲存路徑在啟用期間仍可操作。

程式啟動時預設未啟用熱鍵。手動啟用後，綁定按鍵全域攔截，放開時執行動作，不再依遊戲前景自動啟停。

設定檔位於 `%LOCALAPPDATA%\HD2\bindings.json`，使用 version 2 格式。未綁定的表格列仍會儲存，但不註冊快捷鍵。

## 按鍵名稱

設定中的 `key` 維持字串格式，程式依 scan code 與 `is_keypad` 區分實體按鍵：

| 名稱 | 按鍵 |
| --- | --- |
| `3` | 主鍵盤上排數字 3 |
| `num 3` | 數字鍵盤 3 |
| `page down` | 獨立 Page Down |
| `enter` / `num enter` | 主鍵盤 Enter / 數字鍵盤 Enter |

數字鍵盤錄製為 `num ...`，支援 0～9、小數點、加減乘除與 Enter。Num Lock 切換不改變綁定的實體按鍵身分。`num ...` 是本專案解析的格式。

## HUD 與聊天

「HUD overlay」獨立控制顯示，不受「啟用」勾選狀態影響。HUD 置頂並橫向顯示目前設定的戰略配備圖示與對應按鍵，無 SVG 時顯示名稱。初始位置為螢幕左下角，位置計算包含工作列區域，可拖曳移動。

聊天輸入視窗大小為 200 × 50，開啟時放在螢幕可用區域右下角並嘗試聚焦。Enter 送出、Esc 取消；送出前先切回原視窗，確認前景 HWND 符合後才輸入文字。這是按需查詢與切換視窗，不是遊戲前景監聽。

預設聊天文字與聊天視窗共用 `send_chat()`：開啟遊戲聊天後，每段最多輸入 10 個 Python 字元，每段後等待 0.05 秒，最後按 Enter 送出整則訊息。

## 預估冷卻倒數

同時勾選「HUD overlay」與「預估cd」後，觸發 Stratagem 熱鍵會依 `cooldown` 秒數開始預估倒數，圖示中央顯示 `分:秒`。再次觸發同一 Stratagem 會重新計時；同一 Stratagem 綁定多個按鍵時，共用倒數。`cooldown = 0` 不啟動倒數。

取消「預估cd」會停止更新並清除全部倒數，重新勾選不恢復。取消「HUD overlay」只隱藏 HUD 並停止接受新的倒數觸發，既有倒數繼續，重新顯示時呈現剩餘時間。取消熱鍵「啟用」只解除綁定，既有倒數繼續。倒數不確認投擲或呼叫是否成功，也不套用遊戲中的冷卻修正。

## 執行紀錄

日誌寫入 `%LOCALAPPDATA%\HD2\output.log`，使用 UTF-8，持續追加，不輪替、不自動清除。有 console 時同時輸出至 console；`--noconsole` 打包時只寫檔。

紀錄包含時間、等級、程序與執行緒、模組名稱，以及啟動環境、設定讀寫、綁定啟停、HUD 狀態、巨集開始與完成。聊天正常紀錄只保存字數，不保存全文；例外保存 traceback。第三方套件直接使用的 `print()` 不會自動寫入此檔案。輸入事件送出完成不代表遊戲已確認接收。
