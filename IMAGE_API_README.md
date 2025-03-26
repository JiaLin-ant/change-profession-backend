# 图像生成 API 使用指南

本项目使用 Cloudflare 的 Stable Diffusion XL 模型提供高质量的 AI 图像生成功能。

## API 访问方式

### 1. 直接通过 HTTP 请求调用

```bash
curl -X POST https://your-vercel-domain.com/api/image \
  -H "Content-Type: application/json" \
  -d '{"prompt":"美丽的中国山水画"}'
```

返回的 JSON 格式如下：

```json
{
  "success": true,
  "image": "base64编码的图像数据",
  "prompt": "美丽的中国山水画"
}
```

### 2. 使用提供的工具脚本

我们提供了两种便捷的方式来生成图片：

#### 使用 Shell 脚本

```bash
# 使脚本可执行
chmod +x generate_image.sh

# 运行脚本生成图片
./generate_image.sh "漫步在迷人的秋天森林小径上"
```

#### 使用 Python 脚本

```bash
# 安装所需依赖
pip install requests

# 运行脚本生成图片
python image_curl.py "未来科技城市的日落景象" --output images
```

## 参数说明

API 接受以下参数：

| 参数 | 类型 | 必须 | 描述 |
|------|------|------|------|
| prompt | 字符串 | 是 | 图像生成提示词，可以非常详细地描述您想要生成的图像 |

## 注意事项

1. 图像生成需要几秒钟时间，请耐心等待
2. 图像将以高质量 PNG 格式返回
3. 生成的图像是无水印的，可以直接用于您的项目
4. API 依赖于 Cloudflare Workers AI，确保 API 密钥和账户 ID 有效

## 提示词技巧

为了获得最佳结果，请尝试以下提示词技巧：

- 使用详细的描述，包括风格、颜色、氛围等
- 可以指定艺术风格，如"水彩画风格"、"油画风格"等
- 添加"高质量"、"精细细节"等词语可以提高图像质量
- 避免过于复杂的场景描述

## 本地测试

在部署到 Vercel 之前，可以在本地测试：

```bash
# 启动本地开发服务器
vercel dev

# 测试图像生成
curl -X POST http://localhost:3000/api/image \
  -H "Content-Type: application/json" \
  -d '{"prompt":"测试提示词"}'
``` 