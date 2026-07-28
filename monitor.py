import os
import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 從環境變數讀取金鑰資訊
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")
TARGET_URL = "https://shop.funbox.com.tw/categories/XI/KB"
HISTORY_FILE = "known_products.txt"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_line_msg(message):
    try:
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=message))
    except Exception as e:
        print(f"LINE 發送失敗: {e}")

def load_known_products():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_known_products(products):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        for item in products:
            f.write(f"{item}\n")

def get_current_products():
    try:
        res = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        products = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            title = a_tag.get_text(strip=True)
            if "/products/" in href or "/product/" in href:
                products.add(title if title else href)
        return products
    except Exception as e:
        print(f"抓取失敗: {e}")
        return None

def main():
    known_products = load_known_products()
    current_products = get_current_products()

    if current_products is None:
        return

    # 首次執行，先建立紀錄檔
    if not known_products:
        print("初始化紀錄檔...")
        save_known_products(current_products)
        return

    new_items = current_products - known_products

    if new_items:
        print(f"發現 {len(new_items)} 項新商品！")
        for item in new_items:
            msg = f"🚨 Funbox 新商品上架！\n\n📦 商品：{item}\n🔗 連結：{TARGET_URL}"
            send_line_msg(msg)
        
        # 更新並存檔
        known_products.update(new_items)
        save_known_products(known_products)
    else:
        print("沒有發現新商品。")

if __name__ == "__main__":
    main()
