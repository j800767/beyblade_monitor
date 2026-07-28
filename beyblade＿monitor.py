import time
import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage

# ===== 請替換成你的資訊 =====
LINE_ACCESS_TOKEN = 'BauwWM9BdztmwHbWeCYDFizHvyLpYa/5c/BAv7eLHCRzc3sDnhkisOKVHP2Se68nrIpoCLKYbHQ+mlnUMdHF6ThQ8psqAW9EfWylcOeYKMzQVexI4Y5N6YiCcunWZzpDJHeZNfrb8XuOazd+5P/CHQdB04t89/1O/w1cDnyilFU='
LINE_USER_ID = 'U412b9f83d42cb4c1a1d289d6bd6e3d02'
TARGET_URL = "https://shop.funbox.com.tw/categories/XI/KB"

# 初始化 LINE API
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 模擬瀏覽器 Header，避免被擋
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_line_msg(message):
    """發送 LINE 訊息通知"""
    try:
        line_bot_api.push_message(
            LINE_USER_ID,
            TextSendMessage(text=message)
        )
    except Exception as e:
        print(f"發送 LINE 訊息失敗: {e}")

def get_product_list():
    """爬取當前頁面的商品清單"""
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        products = set()
        
        # 搜尋包含商品連結或名稱的元素
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            title = a_tag.get_text(strip=True)
            # 判斷是否為商品頁連結
            if "/products/" in href or "/product/" in href:
                product_name = title if title else href
                products.add(product_name)
                
        return products
    except Exception as e:
        print(f"抓取網站失敗: {e}")
        return None

def main():
    print("🚀 開始監控 Funbox 商品頁面 (LINE 通知版)...")
    send_line_msg("✅ Funbox 戰鬥陀螺新品 LINE 監控服務已成功啟動！")
    
    # 第一次執行先記錄目前已有的商品
    known_products = get_product_list()
    if known_products is None:
        known_products = set()
    print(f"初始商品數量：{len(known_products)} 件")

    while True:
        # 每 5 分鐘檢查一次（可自行調整秒數，300 秒 = 5 分鐘）
        time.sleep(300) 
        
        current_products = get_product_list()
        if current_products is None:
            continue

        # 比對是否有新上架的商品
        new_items = current_products - known_products
        
        if new_items:
            print(f"🎉 發現 {len(new_items)} 項新商品上架！")
            for item in new_items:
                msg = (
                    f"🚨 Funbox 有新商品上架囉！\n\n"
                    f"📦 商品：{item}\n"
                    f"🔗 連結：{TARGET_URL}"
                )
                send_line_msg(msg)
            
            # 更新已知商品清單
            known_products.update(new_items)
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 檢查完成，無新商品。")

if __name__ == "__main__":
    main()