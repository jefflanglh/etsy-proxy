import requests
from flask import Flask, request
import re
import time

app = Flask(__name__)
ANT_API_KEY = "10f24def57b343d2872fffac037670cf"

@app.route('/')
def get_sales():
    shop_name = request.args.get('shop')
    if not shop_name: return "No shop name"
    
    # 强制加上随机后缀防止缓存
    target_url = f"https://www.etsy.com/shop/{shop_name}?ref=simple-shop-header-name"
    proxy_url = f"https://api.scrapingant.com/v2/general?url={target_url}&x-api-key={ANT_API_KEY}&browser=false"
    
    # 我们只尝试 2 次，但单次等待时间拉长到 8 秒
    for attempt in range(2):
        try:
            response = requests.get(proxy_url, timeout=40)
            
            if response.status_code == 423:
                time.sleep(8) # 暴力等待，强制释放并发位
                continue
            
            if response.status_code == 200:
                html = response.text
                # 针对 Etsy 的多种 HTML 结构进行地毯式搜索
                # 模式1: 数字 sales (如 1,234 sales)
                match = re.search(r'([\d,]+)\s*[Ss]ales', html)
                if match:
                    return match.group(1).replace(',', '')
                
                # 模式2: 纯数字 (可能在特定 class 里)
                match_alt = re.search(r'(\d+)\s*<[^>]*>[Ss]ales', html)
                if match_alt:
                    return match_alt.group(1)
                
                return "0"
            
            return f"HTTP_{response.status_code}"
            
        except Exception as e:
            time.sleep(5)
            
    return "SERVER_BUSY_RETRY_LATER"

def handler(event, context):
    return app(event, context)
