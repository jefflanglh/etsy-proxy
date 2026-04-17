import requests
from flask import Flask, request
import re
import time

app = Flask(__name__)

# 你的 ScrapingAnt API Token
ANT_API_KEY = "10f24def57b343d2872fffac037670cf"

@app.route('/')
def get_sales():
    # 获取 URL 中的 shop 参数，例如 ?shop=lezyicom
    shop_name = request.args.get('shop')
    if not shop_name:
        return "Error: No shop name provided"
    
    # 使用标准 .com 域名，减少地区重定向干扰
    target_url = f"https://www.etsy.com/shop/{shop_name}"
    
    # 构建 ScrapingAnt 请求 URL
    # browser=false 响应最快，节省额度
    proxy_url = f"https://api.scrapingant.com/v2/general?url={target_url}&x-api-key={ANT_API_KEY}&browser=false"
    
    # 针对免费版 1 个并发限制的自动重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(proxy_url, timeout=20)
            
            # 如果触发并发限制 (423)，等待 3 秒后重试
            if response.status_code == 423:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                else:
                    return "Error: System Busy (423 Concurrency Limit)"
            
            # 如果请求成功
            if response.status_code == 200:
                html_content = response.text
                
                # 使用正则表达式匹配销量，兼容 "123 sales" 或 "1,234 Sales"
                # Etsy 的源码中通常显示为 "XXXX sales"
                match = re.search(r'([\d,]+)\s*(?:sales|Sales)', html_content)
                
                if match:
                    # 提取第一组匹配值，并移除数字中的逗号
                    sales_count = match.group(1).replace(',', '')
                    return sales_count
                else:
                    # 如果匹配不到，可能是新店 0 销量，或者结构极其特殊
                    return "0"
            
            # 其他 HTTP 错误
            return f"Error: Proxy Status {response.status_code}"
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return f"Error: {str(e)}"

    return "Error: Unknown failure"

# Vercel Serverless 环境必需的 Handler
def handler(event, context):
    return app(event, context)
