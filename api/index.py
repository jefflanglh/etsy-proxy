import requests
from flask import Flask, request
import re
import time
import random

app = Flask(__name__)
ANT_API_KEY = "10f24def57b343d2872fffac037670cf"

@app.route('/')
def get_sales():
    shop_name = request.args.get('shop')
    if not shop_name: return "Error: No shop name"
    
    target_url = f"https://www.etsy.com/shop/{shop_name}"
    proxy_url = f"https://api.scrapingant.com/v2/general?url={target_url}&x-api-key={ANT_API_KEY}&browser=false"
    
    # 增加到 5 次尝试，每次间隔加长
    for attempt in range(5):
        try:
            response = requests.get(proxy_url, timeout=30)
            
            if response.status_code == 423:
                # 随机等待 4-6 秒，彻底避开并发峰值
                time.sleep(5 + random.uniform(0, 1))
                continue
            
            if response.status_code == 200:
                html = response.text
                # 修改正则：Etsy 源码里有时是 "1,234 sales" 有时在 <span> 里
                # 我们找数字后面紧跟 sales 的组合
                match = re.search(r'([\d,]+)\s*[Ss]ales', html)
                if match:
                    return match.group(1).replace(',', '')
                return "0"
            
            return f"Error: Status {response.status_code}"
            
        except Exception as e:
            time.sleep(3)
            if attempt == 4: return f"Error: {str(e)}"
            
    return "Error: Concurrency Timeout"

def handler(event, context):
    return app(event, context)
