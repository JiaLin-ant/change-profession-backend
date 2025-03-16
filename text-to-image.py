import requests
import urllib.parse
import os
from typing import Optional, Dict, Union

class PollinationsAI:
    """A simple client for the Pollinations.AI image generation API"""
    
    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt/"
    
    def generate_image(self, prompt: str, save_path: Optional[str] = None) -> Dict[str, Union[bool, str]]:
        """
        Generate an image from a text prompt using Pollinations.AI
        
        Args:
            prompt (str): The text prompt to generate the image
            save_path (str, optional): Path to save the generated image
            
        Returns:
            dict: A dictionary containing the status and results
        """
        try:
            # URL encode the prompt
            encoded_prompt = urllib.parse.quote(prompt)
            image_url = self.base_url + encoded_prompt
            
            # Verify if the URL is accessible
            response = requests.head(image_url)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to generate image: Status code {response.status_code}"
                }
            
            result = {
                "success": True,
                "image_url": image_url,
                "prompt": prompt
            }
            
            # Save the image if a path is provided
            if save_path:
                if self._save_image(image_url, save_path):
                    result["saved_path"] = save_path
                else:
                    result["save_error"] = "Failed to save image"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _save_image(self, url: str, filename: str) -> bool:
        """
        Download and save an image from a URL
        
        Args:
            url (str): The URL of the image
            filename (str): The path where to save the image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            return False
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            return False

def main():
    # 创建 PollinationsAI 客户端
    client = PollinationsAI()
    
    # 示例提示词
    prompts = [
        "conceptual isometric world of pollinations ai surreal hyperrealistic digital garden",
        "beautiful sunset over mountains in watercolor style",
        "cyberpunk city at night with neon lights and flying cars"
    ]
    
    # 为每个提示词生成图片
    for i, prompt in enumerate(prompts, 1):
        print(f"\n生成图片 {i}/{len(prompts)}")
        print(f"提示词: {prompt}")
        
        # 生成图片并保存
        result = client.generate_image(
            prompt=prompt,
            save_path=f"generated_image_{i}.jpg"
        )
        
        # 显示结果
        if result["success"]:
            print("✓ 图片生成成功！")
            print(f"图片 URL: {result['image_url']}")
            if "saved_path" in result:
                print(f"图片已保存至: {result['saved_path']}")
        else:
            print("✗ 图片生成失败")
            print(f"错误信息: {result.get('error', '未知错误')}")
        
        print("-" * 50)

if __name__ == "__main__":
    main()
