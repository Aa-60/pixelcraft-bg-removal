# PixelCraft - AI 智能抠图

基于 BiRefNet 大模型的智能抠图工具，支持单张/批量处理、前后对比预览、自由换背景。

## 功能特性

- 单张图片抠图 + 实时前后对比
- 批量处理（最多 100 张）
- 自由更换背景颜色（透明 / 白 / 黑 / 彩色 / 自定义）
- 多格式导出（PNG / JPG / WEBP）
- 一键下载 ZIP 压缩包
- 响应式界面，支持移动端

## 项目结构

```
.
├── app.py                 # Flask 后端主程序
├── templates/
│   └── index.html         # 前端页面
├── requirements.txt       # Python 依赖
├── .gitignore
└── models/                # 模型文件目录（需手动下载，见下方说明）
```

## 模型文件说明

本项目使用 **BiRefNet** 模型进行高精度抠图。由于模型文件较大（约 170MB），未包含在仓库中。

首次运行时，`rembg` 会自动从网络下载 **BiRefNet** 模型到 `models/` 目录。也可以手动下载：

```bash
# 创建模型目录
mkdir models

# 下载 BiRefNet 模型（通用版）
# 首次运行 app.py 时会自动下载，或从 rembg 官方渠道获取
```

> 模型下载地址由 rembg 库自动管理，首次启动需要联网下载，下载完成后可离线使用。

## 本地运行

### 1. 克隆仓库

```bash
git clone https://github.com/yourname/pixelcraft.git
cd pixelcraft
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python app.py
```

服务默认运行在 `http://localhost:5000`

### 可选参数

```bash
python app.py --port=8080          # 自定义端口
python app.py --host=127.0.0.1     # 仅本地访问
```

## 技术栈

- **后端**: Flask + Python
- **模型**: BiRefNet (via rembg)
- **图像处理**: Pillow, ONNX Runtime
- **前端**: 原生 HTML + CSS + JavaScript

## 部署到服务器（未来计划）

等项目买了服务器后，可以直接：

1. 服务器上安装 Python 环境
2. `git clone` 本仓库
3. 安装依赖
4. 用 `gunicorn` 或 `uwsgi` 运行
5. Nginx 反向代理

---

> 当前阶段：代码已整理到 GitHub，等购置服务器后正式上线运营。
