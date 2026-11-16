import datetime
import json
import requests

def fetch_all_data():
    print("🚀 開始從台灣證交所官方 API 抓取「全台股上市」盤後資料...")
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 呼叫證交所官方公開的「所有股票每日收盤行情」API (包含台股所有上市股票)
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    try:
        response = requests.get(url, timeout=15)
        twse_data = response.json()
    except Exception as e:
        print(f"❌ 無法連線至證交所 API: {e}")
        return

    # 為了方便前端分類，我們可以建立一個簡單的產業對應清單 (或者將全部上市股票統一歸類)
    # 這裡我們自動把官方資料轉成結構化格式
    all_stocks = []
    for item in twse_data:
        code = item.get('Code', '')
        name = item.get('Name', '').strip()
        
        # 過濾掉權證或奇怪的代號，只要 4 位數的股票代號
        if len(code) == 4 and code.isdigit():
            try:
                price = float(item.get('ClosingPrice', 0).replace(',', ''))
                change = float(item.get('Change', 0).replace(',', ''))
                prev_close = price - change if price else 0
                change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
                volume = item.get('TradeVolume', '0')
            except:
                price, change, change_pct, volume = 0, 0, 0, "0"

            stock_obj = {
                "code": code,
                "name": name,
                "price": price,
                "change": change,
                "changePct": change_pct,
                "volume": volume,
                "weekChangePct": 0.0, # 預設本週漲幅
                "pe": 15.0,           # 預設本益比
                "yieldPct": 3.0,      # 預設殖利率
                "eps": 5.0,           # 預設 EPS
                "institutional": [
                    {"date": "最新", "foreign": "+500", "trust": "+100", "dealer": "-50"}
                ],
                "dividends": [{"year": "2024", "cash": 2.0}],
                "epsHistory": [{"year": "2024", "val": 5.0}],
                "news": [{
                    "title": f"{name} ({code}) 近期市場動態速覽",
                    "date": current_time.split()[0],
                    "url": "#"
                }]
            }
            all_stocks.append(stock_obj)

    # 為了讓前端好分類，我們暫時把全台股放在「全部上市股票」大分類中
    database = {
        "全台股上市精選": all_stocks
    }

    output_data = {
        "metadata": {
            "lastUpdate": f"{current_time} (全台股自動更新)"
        },
        "database": database
    }
    
    with open("stock_data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print(f"✅ 成功抓取並產出 {len(all_stocks)} 檔台股上市股票資料到 stock_data.json！")

if __name__ == "__main__":
    fetch_all_data()