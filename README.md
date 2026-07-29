# PixelCraft - AI 智能抠图

基于 BiRefNet 大模型的在线智能抠图工具，支持单张和批量处理。

## 功能

- 单张图片抠图 + 实时预览
- 批量处理（最多 100 张）
- 自由更换背景颜色（透明 / 白 / 黑 / 彩色）
- 多格式导出（PNG / JPG / WEBP）
- 一键下载 ZIP 压缩包

## 部署

本项目针对 [Streamlit Cloud](https://streamlit.io/cloud) 优化部署。

### 文件说明

| 文件 | 说明 |
|------|------|
| `streamlit_app.py` | 主应用入口 |
| `requirements.txt` | Python 依赖包 |

### 快速开始

1. Fork 本仓库或推送到你的 GitHub 仓库
2. 登录 [Streamlit Cloud](https://streamlit.io/cloud)
3. 点击 **New app** → 选择本仓库 → 确认部署
4. 等待模型首次加载（约 30-60 秒）

## 技术栈

- Streamlit
- rembg (BiRefNet 模型)
- Pillow
- ONNX Runtime
