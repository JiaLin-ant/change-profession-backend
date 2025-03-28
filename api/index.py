from http.server import BaseHTTPRequestHandler
import os
import json
import requests
from datetime import datetime
import base64
import urllib.parse

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        # 读取请求体
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 解析 JSON 数据
        try:
            data = json.loads(post_data)
            # 处理图像生成请求
            self.handle_image_generation(data)
                
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
            return

    def handle_image_generation(self, data):
        # 从请求中获取提示词
        prompt = data.get("prompt", "")
        if not prompt:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Prompt is required"}).encode('utf-8'))
            return
            
        try:
            # 调用 Cloudflare Stable Diffusion API 生成图像
            image_result = self.generate_image(prompt)
            
            if image_result and "image_data" in image_result:
                # 返回成功结果
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                # 创建返回数据（包含base64编码的图片和其他相关信息）
                response_data = {
                    "success": True,
                    "image": image_result["image_data"],
                    "prompt": prompt
                }
                
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            else:
                # 返回错误信息
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": image_result.get("error", "Unknown error occurred")
                }).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode('utf-8'))
    
    def generate_image(self, prompt):
        # API 配置
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "5dff61c28ee86b9ca69d881fb1cfa207")
        api_key = os.getenv("CLOUDFLARE_API_KEY", "2UR7AkGIEyeqIYoTbr1NFw58Z1aiJNNlvrMkGgSs")
        api_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"

        # 设置请求头
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 设置请求数据
        data = {
            "prompt": prompt,
            "negative_prompt": "ugly, tiling, poorly drawn face, deformed face, deformed eyes, deformed mouth, deformed hair, deformed body, deformed hands, deformed fingers, deformed toes, deformed ears, deformed tail, deformed antenna, deformed horns, deformed claws, deformed wings",
            "width": 512,
            "height": 512,
            "num_steps": 5,
        }

        try:
            # 发送请求
            response = requests.post(api_url, headers=headers, json=data)
            
            # 检查响应状态
            if response.status_code == 200:
                # 获取二进制图片数据并转换为base64
                image_data = base64.b64encode(response.content).decode('utf-8')
                
                return {
                    "success": True,
                    "image_data": image_data
                }
            else:
                return {
                    "success": False,
                    "error": f"API 返回状态码 {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }