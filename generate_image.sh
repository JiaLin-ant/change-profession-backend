#!/bin/bash

# 检查是否提供了提示词参数
if [ -z "$1" ]; then
    echo "用法: ./generate_image.sh \"图片提示词\""
    exit 1
fi

# 提示词
PROMPT="$1"

# API URL（需要更改为您的实际部署URL）
API_URL="http://localhost:3000/api/image"

# 生成时间戳作为文件名
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="image_${TIMESTAMP}.png"

echo "正在生成图片: \"$PROMPT\"..."

# 发送请求并处理响应
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\":\"$PROMPT\"}")

# 检查是否成功
success=$(echo "$response" | grep -o '"success":true' || echo "")

if [ -n "$success" ]; then
    # 从JSON响应中提取base64图片数据
    echo "$response" | 
        grep -o '"image":"[^"]*"' | 
        sed 's/"image":"//;s/"$//' | 
        base64 --decode > "$OUTPUT_FILE"
    
    echo "✓ 图片生成成功！已保存到: $OUTPUT_FILE"
else
    # 提取错误信息
    error=$(echo "$response" | grep -o '"error":"[^"]*"' | sed 's/"error":"//;s/"$//' || echo "未知错误")
    echo "✗ 图片生成失败: $error"
    exit 1
fi 