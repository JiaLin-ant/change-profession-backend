# AI 图像生成服务

本项目使用 Cloudflare 的 Stable Diffusion XL 模型提供高质量的 AI 图像生成功能，无水印，支持多种风格和场景描述。

## API 访问方式

### 1. 直接通过 HTTP 请求调用

```bash
curl -X POST https://change-profession-backend.vercel.app/api \
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

## 图像生成提示词技巧

为了获得最佳效果，推荐使用详细的提示词：

### 风格描述

- 水彩画风格、油画风格、概念艺术、照片级写实感、动漫风格
- 超现实主义、赛博朋克、蒸汽朋克、复古风格、未来主义

### 质量描述

- 高清晰度、4K分辨率、细节丰富、精细刻画
- 专业摄影、精美渲染、高质量

### 构图与视角

- 正面视角、鸟瞰图、俯视图、特写镜头
- 全身照、肖像、风景、全景图

### 光照与色调

- 日落、黎明、蓝色调、金色调、霓虹灯
- 柔和光线、强烈对比、阴影效果、体积光

### 示例提示词

```
"一只可爱的红色熊猫坐在竹林中，身边是翠绿的竹子，阳光透过树叶洒在它身上，照片级写实风格，高清晰度，精美细节"

"未来科技感的中国城市夜景，霓虹灯和全息投影，赛博朋克风格，暖色调与蓝色调对比，高楼大厦，空中飞行的车辆，4K超高清"
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