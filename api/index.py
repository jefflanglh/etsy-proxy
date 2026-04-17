from flask import Flask, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def get_sales():
    shop_name = request.args.get('shop')
    if not shop_name:
        return "Error: No shop name"
    
    url = f"https://www.etsy.com/shop/{shop_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code}"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        # Etsy 目前销量所在的 HTML 结构通常包含 "sales" 关键字
        # 我们尝试寻找包含 "sales" 的 span 标签
        sales_element = soup.find("span", string=lambda t: t and "sales" in t.lower())
        
        if sales_element:
            sales_text = sales_element.text.lower().replace("sales", "").replace(",", "").strip()
            return sales_text
        return "Not Found"
    except Exception as e:
        return f"Error: {str(e)}"

# Vercel 需要这个
def handler(event, context):
    return app(event, context)
