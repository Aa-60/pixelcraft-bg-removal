---
title: PixelCraft AI 抠图
emoji: 📷
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# PixelCraft - AI 智能抠图

基于 BiRefNet 大模型的智能抠图工具，支持单张/批量处理、前后对比预览、自由换背景。

## 功能特性

- 单张图片抠图 + 实时前后对比
- 批量处理（最多 100 张）
- 自由更换背景颜色（透明 / 白 / 黑 / 彩色 / 自定义）
- 多格式导出（PNG / JPG / WEBP）
- 一键下载 ZIP 压缩包
- 响应式界面，支持移动端

## 技术栈

- **后端**: Flask + Python
- **模型**: BiRefNet (via rembg)
- **图像处理**: Pillow, ONNX Runtime
- **前端**: 原生 HTML + CSS + JavaScript

## 模型说明

本项目使用 **BiRefNet** 模型进行高精度抠图。模型文件（约 170MB）不包含在仓库中，首次运行时自动从网络下载。

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（默认 7860 端口）
python app.py

# 自定义端口
python app.py --port=5000
```

访问 `http://localhost:7860`
