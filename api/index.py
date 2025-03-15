from http.server import BaseHTTPRequestHandler
import os
import json
from groq import Groq

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        # 读取请求体
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 解析 JSON 数据
        try:
            data = json.loads(post_data)
            user_message = data.get("messages", [{}])[0].get("content", "")
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
            return

        # 初始化 Groq 客户端
        client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),  # 从环境变量中读取API Key
        )

        # 调用 Groq API
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ],
                model="llama-3.3-70b-versatile",
                stream=False  # 关闭流式模式
            )

            # 收集完整响应
            response_content = chat_completion.choices[0].message.content

            # 返回纯文本结果
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response_content.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
        return