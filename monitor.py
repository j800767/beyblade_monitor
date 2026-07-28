import os
import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 讀取環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

TARGET_URL = "https://shop.funbox.com.tw/categories/XI/KB"
HISTORY_FILE = "known_products.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_line_msg(message):
    """發送 LINE 通知"""
    if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_USER_ID:
        print("⚠️ 未設定 LINE Token 或 User ID")
        return
    try:
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=message))
        print("✅ LINE 訊息發送成功")
    except Exception as e:
        print(f"❌ LINE 發送失敗: {e}")

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
        print(f"網站爬取失敗: {e}")
        return None

def main():
    known_products = load_known_products()
    current_products = get_current_products()

    if current_products is None:
        print("⚠️ 無法取得網頁商品資料")
        return

    # 首次啟動（找不到 known_products.txt 時）
    if not known_products:
        print("🚀 首次啟動監控，紀錄目前商品並發送測試通知...")
        save_known_products(current_products)
        
        # 發送啟動測試簡訊給你的 LINE
        startup_msg = (
            f"✅ <b>Funbox 監控系統已成功啟動！</b>\n\n"
            f"📊 目前追蹤商品數：{len(current_products)} 件\n"
            f"⏱️ 系統運作正常，每 15 分鐘將自動檢查是否有新品。"
        )
        send_line_msg(startup_msg)
        return

    # 比對新品
    new_items = current_products - known_products

    if new_items:
        print(f"🎉 發現 {len(new_items)} 項新商品！發送 LINE 通知...")
        for item in new_items:
            msg = (
                f"🚨 Funbox 有新商品上架囉！\n\n"
                f"📦 商品：{item}\n"
                f"🔗 連結：{TARGET_URL}"
            )
            send_line_msg(msg)
        
        # 更新並儲存歷史清單
        known_products.update(new_items)
        save_known_products(known_products)
    else:
        print("沒有發現新商品。")

if __name__ == "__main__":
    main()
