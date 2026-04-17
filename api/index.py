from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import random

app = Flask(__name__)

@app.route('/')
def get_sales():
    shop_name = request.args.get('shop')
    if not shop_name:
        return "Error: No shop name"
    
    url = f"https://www.etsy.com/shop/{shop_name}"
    
    # 使用更真实的浏览器头信息
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # 使用 Session 保持会话，模拟真实浏览器
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code}"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 针对 Etsy 目前的页面结构寻找销量
        # 尝试寻找包含 "sales" 的 span 或 div
        sales_element = soup.find(lambda tag: tag.name in ['span', 'div'] and "sales" in tag.text.lower() and tag.get('class') != None)
        
        if not sales_element:
             # 备用方案：直接正则匹配网页文本
             import re
             match = re.search(r'(\d+[,.]?\d*)\s*sales', response.text, re.IGNORECASE)
             if match:
                 return match.group(1).replace(",", "")
             return "Not Found"

        sales_text = sales_element.text.lower().replace("sales", "").replace(",", "").strip()
        return sales_text
        
    except Exception as e:
        return f"Error: {str(e)}"

def handler(event, context):
    return app(event, context)
