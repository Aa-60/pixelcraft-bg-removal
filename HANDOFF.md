# 交接文档 — PixelCraft AI 抠图部署任务

> 本文档写给一个完全没有上下文的新会话。请仔细阅读后再继续工作。

---

## 一、项目概述

**项目名称**：PixelCraft - AI 智能抠图

**用户目标**：将本地 Flask 抠图工具部署上线，获得一个永久可访问的 URL，准备拿去闲鱼卖。当前阶段：先免费部署上线，模型保持 BiRefNet 不变，等赚到钱后再买正式服务器。

**技术栈**：
- 后端：Flask + Python 3.10
- 模型：BiRefNet（via rembg 库，首次运行时自动下载约 170MB 的 ONNX 模型文件）
- 图像处理：Pillow, ONNX Runtime
- 前端：原生 HTML + CSS + JavaScript（单文件，约 437 行）
- 部署方式：Docker

**项目路径**（工作区）：
```
C:\Users\Administrator\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a5addad9f9406373a7b62a5
```

**原始项目路径**（D 盘，用户本地）：
```
D:\2026年工作文件夹\trade\抠图\
```

---

## 二、已完成的工作

### 1. 项目代码完整就绪
- `app.py` — Flask 后端，BiRefNet 模型，4 个 API 接口（单张抠图、换背景、批量处理、下载）
- `templates/index.html` — 完整前端界面（单张/批量处理、前后对比、换背景、下载）
- `requirements.txt` — 依赖：flask, rembg, onnxruntime, Pillow, numpy
- `Dockerfile` — Docker 构建配置，基于 python:3.10-slim，端口 7860
- `render.yaml` — Render.com 部署配置
- `README.md` — 项目说明（含 HF Spaces 元数据头）
- `.gitignore` — 忽略 models/、缓存、临时文件

### 2. GitHub 仓库已创建并推送成功
- **仓库地址**：https://github.com/Aa-60/pixelcraft-bg-removal
- **GitHub 用户名**：Aa-60
- **可见性**：公开（Public）
- **分支**：main
- **代码已全部推送**，包含 Dockerfile 和 render.yaml
- **GitHub Token**：（已从文档移除，避免触发 GitHub 密钥扫描）

### 3. Git 已安装在系统中
- Git 路径：`D:\Program Files\Git\cmd\git.exe`
- 通过 PowerShell 下载安装了 Git for Windows v2.54.0

### 4. 本地验证通过
- Flask 应用在本地可以正常运行
- BiRefNet 模型正常加载和抠图
- 前后端交互功能完整

---

## 三、当前卡在哪里

### 部署平台遇到了障碍

尝试了 3 个平台，均未成功上线：

#### 尝试 1：Hugging Face Spaces — ❌ 失败
- **原因**：HF Spaces 现在对 Docker 和 Gradio 类型的 Space 都需要 **PRO 订阅**（$9/月）才能创建
- **错误信息**：`402 Payment Required — Static Spaces are free for everyone, but hosting Gradio and Docker Spaces on free cpu-basic requires a PRO subscription`
- **测试结果**：
  - Docker SDK → 402 付费要求
  - Gradio SDK → 402 付费要求
  - Streamlit SDK → HF API 返回 "Invalid option"（不再支持 Streamlit SDK）
  - Static SDK → 可以创建，但无法运行 Python 后端
- **HF Token**：（已移除）
- **HF 用户名**：ya-2026123

#### 尝试 2：Railway — ❌ 失败
- 安装了 Railway CLI（通过 npm install -g @railway/cli）
- Railway CLI 路径：`D:\2026年工作文件夹\trade\.npm-global\node_modules\@railway\cli\bin\railway.exe`
- 尝试了 `railway login` 和 `railway login --browserless` 两种方式
- **问题**：
  - 浏览器授权流程：`railway login` 报 "拒绝访问 (os error 5)"
  - Browserless 流程：设备码生成后，用户在浏览器授权，但授权后 CLI 端未能正确接收 token，提示 "Device code expired" 或 "Unauthorized"
- 可能原因：Railway CLI 的 OAuth 回调在当前 Windows 环境下有权限问题
- **未继续尝试**：可以考虑直接通过 Railway 网页创建项目（类似 Render 的方式）

#### 尝试 3：Render.com — ⏳ 待用户操作
- 已将 `render.yaml` 推送到 GitHub 仓库
- 已向用户提供 Render.com 部署步骤说明
- **用户尚未完成 Render 注册和部署操作**
- Render 免费层：512MB RAM、0.1 vCPU、自动休眠（15分钟无访问后休眠，访问时自动唤醒约30-60秒）
- **潜在风险**：BiRefNet 模型加载需要约 1-2GB 内存，Render 免费层只有 512MB，**可能内存不够**

---

## 四、下一步计划

### 方案 A：Render.com（优先尝试，但可能内存不够）
1. 用户访问 https://dashboard.render.com/register 注册
2. 用 GitHub 账号登录
3. 创建 Web Service，选择 GitHub 仓库 `Aa-60/pixelcraft-bg-removal`
4. Runtime 选 Docker，Instance Type 选 Free
5. 部署并观察是否因内存不足崩溃
6. 如果内存不够 → 转方案 B

### 方案 B：Railway 网页部署（绕过 CLI 问题）
1. 用户访问 https://railway.app 注册/登录
2. New Project → Deploy from GitHub repo
3. 选择 `Aa-60/pixelcraft-bg-removal`
4. Railway 会自动识别 Dockerfile
5. Railway 免费额度：每月 $5 的使用量，内存 512MB（可能也不够）
6. 如果不够 → 考虑 Railway 付费计划或转方案 C

### 方案 C：换用更轻量模型（如果所有免费平台内存都不够）
- 将 BiRefNet 换成 U2Net（约 176MB，内存占用更少）
- 修改 `app.py` 第 50 行：
  ```python
  # 当前：_birefnet_session = new_session(model_name="birefnet-general")
  # 改为：_birefnet_session = new_session(model_name="u2net")
  ```
- 之前在 Streamlit Cloud 上尝试过 U2Net，1GB 内存可以跑
- 但用户明确说过"模型不变"，需要先和用户沟通

### 方案 D：Koyeb 部署
- 免费层：512MB RAM、0.1 vCPU
- 支持 Docker 部署
- https://www.koyeb.com/
- 操作方式类似 Render，从 GitHub 仓库部署

### 方案 E：本地长期运行 + Cloudflare Tunnel
- 用户本地 D 盘已有完整可运行的项目
- 用 Cloudflare Tunnel 暴露到公网（之前做过，URL 会变）
- 缺点：电脑关机就断、URL 不固定
- 用户之前明确不想要这个方案

---

## 五、绝对不要再踩的坑

### 1. Hugging Face Spaces 免费层已不能跑 Docker/Gradio
- **坑**：花费大量时间准备 Dockerfile 和 HF 部署脚本，结果创建时收到 402 付费错误
- **教训**：HF Spaces 在 2026 年已改政策，只有 Static Space 免费，Static 不能运行 Python 后端
- **不要再试** HF Spaces 部署，除非用户愿意付 $9/月 PRO 订阅

### 2. Railway CLI 在当前环境有权限问题
- **坑**：`railway login` 浏览器流程报 "拒绝访问 (os error 5)"，browserless 流程设备码过期
- **教训**：不要再用 Railway CLI，改用 Railway 网页直接操作

### 3. Git 路径问题
- **坑**：Git 安装在 `D:\Program Files\Git\cmd\git.exe`，不是默认的 C 盘
- **教训**：在 PowerShell 中调用 git 时，需要用完整路径或先刷新 PATH

### 4. Python 多行字符串导致 SyntaxError
- **坑**：在 Python 脚本中用多行字符串作为 git commit message，导致 SyntaxError
- **教训**：commit message 保持单行

### 5. Streamlit Cloud 1GB 内存不够跑 BiRefNet
- **坑**：之前尝试过 Streamlit Cloud，BiRefNet 模型加载就 OOM
- **教训**：BiRefNet 需要至少 2GB 内存才能稳定运行；U2Net 需要 1GB

### 6. 不要删除 D 盘原始项目文件
- **坑**：用户之前要求清理 C 盘临时文件时，差点误删 D 盘原始项目
- **教训**：D 盘 `D:\2026年工作文件夹\trade\抠图\` 是用户的原始工作目录，绝对不要动

### 7. Flask 端口必须是 7860（Docker 部署要求）
- **坑**：原 app.py 默认端口 5000，但 Docker 平台（HF/Render）要求 7860
- **当前状态**：已修改为 `port = int(os.environ.get("PORT", 7860))`，通过环境变量适配

### 8. 用户偏好
- 沟通语言：中文
- 不喜欢复杂的后处理（alpha matting 等）
- 抠图质量要求高，边角要干净
- 不喜欢专业摄影光影效果
- 错误提示要友好（红色横幅中文说明，不要 JSON 或 alert）
- 最终交付物要放在 C 盘工作区目录

---

## 六、关键文件和路径速查

| 文件 | 路径 |
|------|------|
| Flask 后端 | 工作区 `app.py` |
| 前端页面 | 工作区 `templates/index.html` |
| Docker 配置 | 工作区 `Dockerfile` |
| Render 配置 | 工作区 `render.yaml` |
| 依赖清单 | 工作区 `requirements.txt` |
| GitHub 仓库 | https://github.com/Aa-60/pixelcraft-bg-removal |
| 原始项目 | `D:\2026年工作文件夹\trade\抠图\` |
| 部署脚本（临时） | `c:\Users\Administrator\.trae-cn\work\6a5addad9f9406373a7b62a8\deploy_hf.py` |
| GitHub 推送脚本（临时） | `c:\Users\Administrator\.trae-cn\work\6a5addad9f9406373a7b62a8\push_github.py` |

**Git 路径**：`D:\Program Files\Git\cmd\git.exe`
**GitHub Token**：（保存在用户记忆中，不写入仓库）
**HF Token**：（保存在用户记忆中，不写入仓库）

---

## 七、新会话接手后的第一步

1. 先和用户确认：**Render.com 注册了吗？部署成功了吗？**
2. 如果 Render 失败（大概率内存不够），立即转向 Railway 网页部署
3. 如果 Railway 也失败，和用户商量是否接受 U2Net 模型（内存占用更低）
4. 或者推荐用户花少量钱买 VPS（如腾讯轻量服务器、搬瓦工等），Docker 一键部署，BiRefNet 无压力

**核心提醒**：代码和 GitHub 仓库都已就绪，唯一卡住的是"找一个免费且内存够用的部署平台"。
