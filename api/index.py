import requests
from flask import Flask, request
import re

app = Flask(__name__)

# 你的 ScrapingAnt API Token
ANT_API_KEY = "10f24def57b343d2872fffac037670cf"

@app.route('/')
def get_sales():
    shop_name = request.args.get('shop')
    if not shop_name:
        return "Error: No shop name"
    
    # 构建指向 Etsy 的目标 URL
    target_url = f"https://www.etsy.com/au/shop/{shop_name}"
    
    # 构建 ScrapingAnt 的请求链接
    # browser=false 可以节省额度，ant_country=au 模拟澳洲访问
    proxy_url = f"https://api.scrapingant.com/v2/general?url={target_url}&x-api-key={ANT_API_KEY}&browser=false&ant_country=au"
    
    try:
        # 向代理商发起请求
        r = requests.get(proxy_url, timeout=25)
        
        if r.status_code != 200:
            return f"Error: Proxy returned {r.status_code}"
        
        html_content = r.text
        
        # 使用正则表达式在 HTML 中寻找销售数字
        # 匹配格式如 "123 sales" 或 "1,234 sales"
        match = re.search(r'([\d,]+)\s*sales', html_content, re.IGNORECASE)
        
        if match:
            # 提取数字并去掉逗号
            sales_count = match.group(1).replace(',', '')
            return sales_count
        else:
            # 如果没找到，可能是新店 0 销量，或者结构变化
            return "0"
            
    except Exception as e:
        return f"Error: {str(e)}"

# Vercel 需要这个处理函数
def handler(event, context):
    return app(event, context)
