import requests
from flask import Flask, request

app = Flask(__name__)

# --- 这里粘贴你刚才生成的 Google 脚本链接 ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxqYobGd-BGA6K0vjonH_REiQ3dkzuZNB3B0HYtgJ3lMwHmVFgEC8tnSp4CYyWCwanV/exec"

@app.route('/')
def get_sales():
    shop_name = request.args.get('shop', 'lezyicom')
    
    # 转发请求给 Google 脚本
    final_url = f"{GOOGLE_SCRIPT_URL}?shop={shop_name}"
    
    try:
        # Google 脚本会自动处理重定向，所以使用 allow_redirects=True
        r = requests.get(final_url, timeout=20, allow_redirects=True)
        return r.text.strip()
    except Exception as e:
        return f"PROXY_ERROR_{str(e)}"

def handler(event, context):
    return app(event, context)
