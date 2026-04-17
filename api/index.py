from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

@app.route('/')
def get_sales():
    shop_name = request.args.get('shop')
    if not shop_name:
        return "Error: No shop name"
    
    url = f"https://www.etsy.com/shop/{shop_name}"
    
    # 极度真实的 Header 伪装
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # 使用 Session 来保持连接特征
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 403:
            return "Error: Etsy blocked the request (403)"
            
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code}"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试多种提取方式，防止 Etsy 修改布局
        # 方式 1: 寻找包含 "sales" 的 span
        sales_element = soup.find("span", string=lambda t: t and "sales" in t.lower())
        
        if not sales_element:
            # 方式 2: 尝试直接找特定的 class (Etsy 常用 wt-text-caption)
            sales_element = soup.select_one('span[class*="sales"]')

        if sales_element:
            sales_text = sales_element.text.lower().replace("sales", "").replace(",", "").strip()
            return sales_text
            
        return "0" # 如果找不到销量元素，可能该店还没有销量
        
    except Exception as e:
        return f"Error: {str(e)}"

def handler(event, context):
    return app(event, context)
