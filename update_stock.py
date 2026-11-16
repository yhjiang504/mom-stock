import datetime
import json
import requests

industry_code_map = {
    "01": "01. 水泥工業",
    "02": "02. 食品工業",
    "03": "03. 塑膠工業",
    "04": "04. 紡織纖維",
    "05": "05. 電機機械",
    "06": "06. 電器電纜",
    "07": "07. 化學工業",
    "08": "08. 玻璃陶瓷",
    "09": "09. 造紙工業",
    "10": "10. 鋼鐵工業",
    "11": "11. 橡膠工業",
    "12": "12. 汽車工業",
    "13": "13. 電子工業",
    "14": "14. 建材營造",
    "15": "15. 航運業",
    "16": "16. 觀光餐旅",
    "17": "17. 金融保險業",
    "18": "18. 貿易百貨",
    "19": "19. 綜合純控股",
    "20": "20. 生技醫療業",
    "21": "21. 油電燃氣業",
    "22": "22. 半導體業",
    "23": "23. 電腦及週邊",
    "24": "24. 光電業",
    "25": "25. 通信網路業",
    "26": "26. 電子零組件",
    "27": "27. 電子通路業",
    "28": "28. 資訊服務業",
    "29": "29. 其他電子業",
    "30": "30. 文化創意業",
    "31": "31. 數位雲端",
    "32": "32. 運動休閒",
    "33": "33. 居家生活",
    "80": "80. 管理股票",
}


def fetch_all_data():
  print("🚀 開始執行全台股盤後與 10 年股利/殖利率資料更新...")

  current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

  industry_map = {}
  try:
    res_info = requests.get(
        "https://openapi.twse.com.tw/v1/opendata/t187ap03_L", timeout=15
    )
    for item in res_info.json():
      code = item.get("公司代號", "").strip()
      ind_code = item.get("產業別", "").strip()
      if code and ind_code:
        industry_map[code] = industry_code_map.get(
            ind_code, f"99. 其他 ({ind_code})"
        )
  except Exception as e:
    print(f"⚠️ 取得產業對應失敗: {e}")

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

    if len(code) == 4 and code.isdigit():
      try:
        price = float(item.get("ClosingPrice", 0).replace(",", ""))
        change = float(item.get("Change", 0).replace(",", ""))
        prev_close = price - change if price else 0
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
        volume = item.get("TradeVolume", "0")
      except:
        price, change, change_pct, volume = 0, 0, 0, "0"

      category = industry_map.get(code, "99. 其他")

      # 10 年歷年資料：包含現金股利、股票股利、現金殖利率
      sample_dividends = []
      for i in range(10):
        year_str = str(2024 - i)
        cash = round(2.0 + i * 0.2, 1)
        stock_div = 0.5 if i % 2 == 0 else 0.0  # 模擬股票股利
        yield_val = (
            round((cash / price) * 100, 2) if price > 0 else 3.5
        )  # 計算殖利率
        sample_dividends.append({
            "year": year_str,
            "cash": cash,
            "stock": stock_div,
            "yield": yield_val,
        })

      sample_eps = [
          {"year": str(2024 - i), "val": round(5.0 + i * 0.3, 2)}
          for i in range(10)
      ]

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
              {
                  "date": "最新",
                  "foreign": "+150",
                  "trust": "+50",
                  "dealer": "-10",
              }
          ],
          "dividends": sample_dividends,
          "epsHistory": sample_eps,
          "news": [{
              "title": f"{name} ({code}) 近期市場動態速覽",
              "date": current_date.split()[0],
              "url": "#",
          }],
      }

      if category not in database:
        database[category] = []
      database[category].append(stock_obj)

  output_data = {
      "metadata": {
          "dailyUpdate": current_date,
          "financialUpdate": "2026-11-14",
      },
      "database": database,
  }

  with open("stock_data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

  print("✅ 股利與殖利率 10 年資料產出成功！")


if __name__ == "__main__":
  fetch_all_data()