#!/usr/bin/env python3
import requests
import json
import base64
import argparse
import os
from datetime import datetime

def generate_and_save_image(prompt, output_dir='.'):
    """
    通过 API 生成图片并保存到本地
    
    Args:
        prompt (str): 图片生成提示词
        output_dir (str): 输出目录，默认为当前目录
    
    Returns:
        str: 保存的图片路径或错误信息
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # API URL（本地开发时用 localhost，部署后用实际域名）
    api_url = "http://localhost:3000/api/image"  # 根据实际情况修改
    
    try:
        # 发送 POST 请求
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json={"prompt": prompt}
        )
        
        # 检查响应状态
        if response.status_code != 200:
            return f"错误: API 返回状态码 {response.status_code}，响应: {response.text}"
        
        # 解析 JSON 响应
        result = response.json()
        
        # 检查响应结构
        if not result.get("success", False):
            return f"错误: {result.get('error', '未知错误')}"
        
        # 获取 base64 图片数据
        image_data = result.get("image")
        if not image_data:
            return "错误: 响应中没有图片数据"
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        output_path = os.path.join(output_dir, filename)
        
        # 将 base64 数据转换为二进制并保存
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image_data))
        
        print(f"✓ 图片生成成功！已保存到: {output_path}")
        print(f"提示词: {prompt}")
        return output_path
        
    except Exception as e:
        return f"错误: {str(e)}"

if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="生成并保存 AI 图片")
    parser.add_argument("prompt", help="图片生成提示词")
    parser.add_argument("--output", "-o", default=".", help="输出目录，默认为当前目录")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 生成并保存图片
    result = generate_and_save_image(args.prompt, args.output)
    
    # 如果返回的是错误信息，打印出来
    if result.startswith("错误:"):
        print(result) 