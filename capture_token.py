#!/usr/bin/env python3
import json
from mitmproxy import http

TOKEN_FILE = "/home/windy/wechat-agent/token.json"

class TokenCapture:
    def response(self, flow: http.HTTPFlow):
        # 捕获所有storeId
        store_id = None
        
        # 从请求参数获取
        if hasattr(flow.request, 'urlencoded_form'):
            store_id = flow.request.urlencoded_form.get("storeId")
        
        # 从请求头获取
        if not store_id:
            store_id = flow.request.headers.get("STOREID")
        
        if store_id:
            print(f"[+] StoreId: {store_id} - {flow.request.url[:80]}")
        
        # 捕获登录token
        if "customeraccount/Auth" in flow.request.url:
            try:
                data = json.loads(flow.response.text)
                if data.get("successed") and data.get("accessToken"):
                    token = data["accessToken"]
                    result = {
                        "token": token,
                        "store_id": store_id or "",
                        "url": flow.request.url
                    }
                    with open(TOKEN_FILE, "w") as f:
                        json.dump(result, f, indent=2)
                    print(f"[+] Token: {token[:20]}...")
            except:
                pass

addons = [TokenCapture()]
