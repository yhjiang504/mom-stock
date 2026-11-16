import datetime
import json
import requests


def fetch_all_data():
  print(
      "🚀 開始從台灣證交所官方 API 抓取「上市公司產業別」與「盤後行情」..."
  )

  current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

  # 1. 取得上市公司基本資料（包含官方產業別對應表）
  industry_map = {}
  try:
    res_info = requests.get(
        "https://openapi.twse.com.tw/v1/opendata/t187ap03_L", timeout=15
    )
    for item in res_info.json():
      code = item.get("公司代號", "").strip()
      industry = item.get("產業別", "").strip()
      if code and industry:
        industry_map[code] = industry
  except Exception as e:
    print(f"⚠️ 取得官方產業別對應失敗: {e}")

  # 2. 取得全台股每日收盤行情
  url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
  try:
    response = requests.get(url, timeout=15)
    twse_data = response.json()
  except Exception as e:
    print(f"❌ 無法連線至證交所行情 API: {e}")
    return

  database = {}

  for item in twse_data:
    code = item.get("Code", "").strip()
    name = item.get("Name", "").strip()

    # 過濾出 4 位數的普通股票代號
    if len(code) == 4 and code.isdigit():
      try:
        price = float(item.get("ClosingPrice", 0).replace(",", ""))
        change = float(item.get("Change", 0).replace(",", ""))
        prev_close = price - change if price else 0
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
        volume = item.get("TradeVolume", "0")
      except:
        price, change, change_pct, volume = 0, 0, 0, "0"

      # 查詢這支股票屬於哪個官方產業（若找不到則歸類為「其他」）
      category = industry_map.get(code, "其他")

      stock_obj = {
          "code": code,
          "name": name,
          "price": price,
          "change": change,
          "changePct": change_pct,
          "volume": volume,
          "weekChangePct": 0.0,
          "pe": 15.0,
          "yieldPct": 3.0,
          "eps": 5.0,
          "institutional": [
              {"date": "最新", "foreign": "+0", "trust": "+0", "dealer": "+0"}
          ],
          "dividends": [{"year": "2024", "cash": 2.0}],
          "epsHistory": [{"year": "2024", "val": 5.0}],
          "news": [{
              "title": f"{name} ({code}) 近期市場動態速覽",
              "date": current_time.split()[0],
              "url": "#",
          }],
      }

      # 依照官方產業分類放入對應的盒子裡
      if category not in database:
        database[category] = []
      database[category].append(stock_obj)

  output_data = {
      "metadata": {
          "lastUpdate": f"{current_time} (官方類別與盤後資料自動更新)"
      },
      "database": database,
  }

  with open("stock_data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

  print(
      f"✅ 成功！已將所有上市股票依官方類別分類完畢，共包含"
      f" {len(database)} 個產業類別，已產出 stock_data.json！"
  )


if __name__ == "__main__":
  fetch_all_data()
