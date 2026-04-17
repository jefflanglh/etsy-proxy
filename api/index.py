import requests
from flask import Flask, request
import re

app = Flask(__name__)
ANT_API_KEY = "10f24def57b343d2872fffac037670cf"

@app.route('/')
def get_sales():
    shop_name = request.args.get('shop')
    if not shop_name: return "Error: No shop name"
    
    # 强制访问澳洲站点路径
    target_url = f"https://www.etsy.com/au/shop/{shop_name}"
    
    # ant_country=au 确保代理服务器也使用澳洲 IP，这样网页内容最准确
    proxy_url = f"https://api.scrapingant.com/v2/general?url={target_url}&x-api-key={ANT_API_KEY}&browser=false&ant_country=au"
    
    try:
        # 设置较长的超时，因为跨国代理可能稍慢
        r = requests.get(proxy_url, timeout=20)
        
        if r.status_code == 423: 
            return "Error: Concurrency limit reached. Wait 10s."
        
        if r.status_code != 200:
            return f"Error: Proxy Status {r.status_code}"
            
        html = r.text
        
        # 针对 Etsy 澳洲站源码的正则优化
        # 匹配像 "12 sales" 或 "123销售" 之类的结构
        match = re.search(r'([\d,]+)\s*(?:sales|Sales)', html)
        
        if match:
            # 提取数字并去掉逗号
            return match.group(1).replace(',', '')
        
        # 如果正则没抓到，尝试备用方案：寻找包含 "sales" 的特定位置
        return "0" 
        
    except Exception as e:
        return f"Error: {str(e)}"

def handler(event, context):
    return app(event, context)
