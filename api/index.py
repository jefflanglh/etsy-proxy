import requests
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/')
def get_sales():
    shop_name = request.args.get('shop', 'lezyicom')
    
    # 这是 Etsy 内部的一个数据接口，通常防御比主页弱
    api_url = f"https://www.etsy.com/api/v3/ajax/public/shop-home/id?shop_name={shop_name}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        # 第一步：尝试获取 Shop ID
        r = requests.get(api_url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            shop_id = data.get('id')
            
            # 第二步：如果拿到了 ID，去另一个更简单的接口拿销量
            if shop_id:
                details_url = f"https://www.etsy.com/api/v3/ajax/public/shop-home/header?shop_id={shop_id}"
                r2 = requests.get(details_url, headers=headers, timeout=10)
                
                # 在返回的乱码（HTML）中暴力搜索数字
                if r2.status_code == 200:
                    import re
                    match = re.search(r'([\d,]+)\s*[Ss]ales', r2.text)
                    if match:
                        return match.group(1).replace(',', '')
            
            return "0"
        else:
            # 如果直接访问被封（403），我们只能退回到代理模式，但这次换一种简单的
            return f"BLOCKED_BY_ETSY_{r.status_code}"
            
    except Exception as e:
        return f"ERROR_{str(e)}"

def handler(event, context):
    return app(event, context)
