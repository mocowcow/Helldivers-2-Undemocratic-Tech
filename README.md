# HD2 Undemocratic Tech

Windows 上的 Helldivers 2 快捷鍵與聊天輔助工具，使用 PySide6、keyboard 及 pydirectinput。

## 專案結構

| 路徑 | 責任 |
| --- | --- |
| `main.py` | 建立應用程式、載入設定、串接元件與釋放快捷鍵 |
| `ui/binding_panel.py` | 分頁導航、收集各頁內容、套用與儲存操作 |
| `ui/binding_table.py` | 戰略配備與聊天綁定的共用表格 |
| `ui/settings_page.py` | 設定檔位置、儲存按鈕與聊天視窗快捷鍵 |
| `ui/key_input.py` | 單一按鍵擷取，Esc 清除綁定 |
| `ui/chat_input.py` | 聊天輸入視窗、輸入法狀態及送出流程 |
| `ui/stratagem_picker.py` | 分類 SVG 選擇視窗，每列 10 個項目 |
| `hotkeys/models.py` | 不依賴 UI 或輸入工具的 Binding 資料模型 |
| `hotkeys/manager.py` | 快捷鍵註冊、移除、替換與失敗還原 |
| `hotkeys/validation.py` | 綁定驗證及排除未綁定項目 |
| `hotkeys/foreground.py` | 將前景變更事件交回 Qt 執行緒，切換快捷鍵註冊 |
| `game/actions.py` | 聊天文字與戰略配備按鍵序列輸入 |
| `game/windows.py` | Win32 宣告、遊戲前景判斷與視窗聚焦 |
| `config/defaults.py` | 預設綁定及輸入間隔 |
| `config/settings.py` | JSON 設定讀寫及原子替換 |
| `stratagems.py` | 戰略配備名稱、分類、指令及 SVG 檔名 |
| `resources.py` | 原始碼與 PyInstaller 封裝環境共用的資源路徑 |
| `stratagems-svg/`、`icon.ico` | UI 圖示資源 |

## 啟動與打包

在專案根目錄安裝 `requirements.txt` 中的依賴，再執行 `python main.py`。
安裝 PyInstaller 後可執行 `build.bat`，其中包含 icon 與 SVG 資源設定。

## 設定行為

「套用」更新所有分頁的執行中綁定，不寫入檔案。「儲存」保存所有分頁的目前內容，不更新執行中綁定。
設定檔位於 `%LOCALAPPDATA%/HD2/bindings.json`，使用 version 2 格式。未綁定的表格列仍會儲存，但不註冊快捷鍵。

只有遊戲在前景時才註冊快捷鍵；按鍵放開時執行動作。聊天輸入視窗維持 Enter 送出、Esc 取消。
