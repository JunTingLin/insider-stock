# 台股內部人持股異動金額爬取

## 專案說明
本專案旨在自動化爬取台灣證券交易所公開資訊觀測站中的內部人持股異動事後申報表。特別關注內部人持股數量的增加，並計算出增加股份的市值。此程式預定於每月固定時間執行，自動化地從[公開資訊觀測站-內部人持股異動事後申報表](https://mops.twse.com.tw/mops/web/query6_1)爬取數據，並將結果保存為 Excel 檔案。

使用[twstock](https://github.com/mlouielu/twstock)開源庫來獲取股票收盤價，並計算指定月份內部人增加持股的總市值。僅當增加股數不為零時，相關數據才會被記錄並展示。

## 功能特色
- **自動化爬取**：每月自動從公開資訊觀測站獲取最新的內部人持股異動數據。
- **數據計算**：計算內部人增加持股的市值。
- **報表匯出**：將爬取和計算的結果匯出為 Excel 檔案，方便進行進一步分析和存檔。
- **自動通知**：程式運行完畢後，會將報表上傳至 Google Drive 並透過 Email 通知使用者。

## 使用說明
1. 將專案克隆到本地環境。
2. 確保 Python 環境已安裝相關依賴，執行 `pip install -r requirements.txt` 安裝所需套件。
3. 訪問 Google Cloud Platform (GCP)，並開啟 Google Drive API。創建一個新的專案，並在 API 和服務中啟用 Google Drive API。
4. 在 API 和服務的憑證頁面中，選擇創建憑證，選擇服務帳戶，並下載 JSON 格式的私鑰。將此私鑰命名為 `service-account-file.json` 並放置於專案根目錄。
5. 根據 `config.ini.example` 創建一個 `config.ini` 檔案，並填寫必要的配置信息，包括服務帳戶的 email 地址和其他必要資訊。
6. 若要使用 Gmail 自動發信功能，訪問您的 Google 帳戶安全設置，啟用「兩步驟驗證」，然後在「應用程式密碼」部分生成一個新的應用程式密碼。將此密碼填寫於 `config.ini` 中的相應欄位。
7. 執行 `main.py` 啟動爬蟲。

### 自動執行設定（Linux）
若需在 Linux 伺服器上配置24小時自動執行，請依照以下步驟操作：

1. 確認機器上已安裝並配置好 `cron` 服務。
2. 使用 `crontab -e` 命令編輯定時任務。
3. 在 `crontab` 文件中添加以下行，設定任務執行時間。以下範例代表每月13日的00時30分執行 `run_python_script.sh` 腳本：

    ```sh
    30 00 13 * * /bin/bash /home/junting/insider-stock/run_python_script.sh > /home/junting/insider-stock/run_python_script.log 2>&1
    ```

    - `> /home/junting/insider-stock/run_python_script.log 2>&1` 語法將標準輸出和標準錯誤輸出都重定向到指定的日誌文件中，方便追蹤執行狀態。

4. 確保 `run_python_script.sh` 腳本具有執行權限：

    ```bash
    chmod +x /home/junting/insider-stock/run_python_script.sh
    ```



## 輸出檔案
匯出的報表將保存在 `output` 資料夾中。報表檔案名稱格式為 `YYYY_MM_insider_stock_changes_TIMESTAMP.xlsx`。

## 欄位說明
- **身份別**：內部人的身份類型，如董事、監事等。
- **姓名**：內部人的姓名。
- **持股種類**：持有的股票種類。
- **本月增加股數(集中市場)**：當月增加的股數。
- **持股增加金額**：根據該月最初獲得的收盤價計算的增加股份市值。

## 截圖示例
(在此處放入報表的截圖sample，讓使用者對輸出格式有直觀的理解)

## 注意事項
- 確保在使用前已經設定好 `config.ini` 和 Google Drive API 的服務帳戶金鑰。
- 本專案僅供學術交流和個人使用，請遵守當地法律法規，尊重數據來源網站的版權和使用條款。

