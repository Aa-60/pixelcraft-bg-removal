# PixelCraft - Streamlit Cloud 部署指南

## 文件已准备就绪

以下文件已创建在本地：

- `streamlit_app.py` - Streamlit 主应用
- `requirements.txt` - Python 依赖
- `README.md` - 项目说明

---

## 推送到 GitHub 步骤

### 1. 登录 GitHub 并创建仓库

1. 访问 https://github.com/new
2. 仓库名称：`pixelcraft-bg-removal`（或你喜欢的名字）
3. 选择 **Public**（公开）
4. 不要勾选 "Add a README file"
5. 点击 **Create repository**

### 2. 在本地推送代码

在 PowerShell 中执行以下命令（已自动完成初始化）：

```powershell
cd 'C:\Users\Administrator\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a5addad9f9406373a7b62a5'

# 连接远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/pixelcraft-bg-removal.git

# 推送代码
git branch -M main
git push -u origin main
```

如果需要登录，按提示输入 GitHub 用户名和密码/Token。

---

## 部署到 Streamlit Cloud

### 1. 登录 Streamlit Cloud

1. 访问 https://streamlit.io/cloud
2. 点击 **Continue with GitHub** 使用 GitHub 账号登录

### 2. 创建新应用

1. 点击 **New app**
2. 在 **Repository** 下拉框中选择 `YOUR_USERNAME/pixelcraft-bg-removal`
3. **Main file path** 填入：`streamlit_app.py`
4. 点击 **Deploy**

### 3. 等待部署完成

- 首次部署需要 2-5 分钟（需要下载依赖和模型）
- 模型首次加载约需 30-60 秒
- 部署成功后，你会获得一个永久 URL（如 `https://pixelcraft-bg-removal-xxxx.streamlit.app`）

---

## 完成！

部署成功后，你将拥有一个 **永久在线、24小时运行** 的 AI 抠图工具！

### 功能特点

- 单张抠图 + 实时预览
- 批量处理（最多 100 张）
- 自由更换背景颜色
- 多格式导出（PNG / JPG / WEBP）
- 一键下载 ZIP

### 注意事项

1. **免费限制**：Streamlit Cloud 免费版有 1GB 内存限制，但对于抠图应用足够使用
2. **休眠机制**：长时间无访问会进入休眠，下次访问时自动唤醒（约需 10-30 秒）
3. **模型缓存**：模型只需首次加载，后续处理速度会更快
