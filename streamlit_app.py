# -*- coding: utf-8 -*-
"""
PixelCraft - AI 智能抠图 (Streamlit版)
BiRefNet 模型 | 单张/批量处理 | 前后对比 | 自由换背景
"""
import os
import io
import zipfile
import base64
import numpy as np

os.environ["U2NET_HOME"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.environ["ONNXRUNTIME_EXECUTION_PROVIDERS"] = "CPUExecutionProvider"

import streamlit as st
from PIL import Image
from rembg import remove, new_session

# ========== 页面配置 ==========
st.set_page_config(
    page_title="PixelCraft - AI 智能抠图",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== 自定义样式 ==========
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        margin: 0;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin-top: 8px;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }
    div[data-testid="stFileUploader"] {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ========== 缓存模型 ==========
@st.cache_resource
def get_session():
    """加载 BiRefNet 模型（只加载一次）"""
    return new_session(model_name="birefnet-general")


def remove_bg(input_image):
    """抠图，返回 RGBA PIL Image"""
    if isinstance(input_image, Image.Image):
        img = input_image.convert("RGBA")
    else:
        img = Image.open(io.BytesIO(input_image)).convert("RGBA")
    out = remove(img, session=get_session())
    if out.mode != "RGBA":
        out = out.convert("RGBA")
    return out


def apply_bg_color(rgba_img, bg_color):
    """给透明图加背景色"""
    if bg_color == "transparent":
        return rgba_img
    bg_rgb = tuple(int(bg_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    bg = Image.new("RGBA", rgba_img.size, bg_rgb + (255,))
    return Image.alpha_composite(bg, rgba_img)


def img_to_download(img, fmt="PNG", filename="result.png"):
    """转换图片为下载链接"""
    buf = io.BytesIO()
    if fmt == "JPEG":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
        bg.save(buf, format="JPEG", quality=95)
    else:
        img.save(buf, format=fmt)
    buf.seek(0)
    return buf


# ========== 主界面 ==========
st.markdown("""
<div class="main-header">
    <h1>📷 PixelCraft - AI 智能抠图</h1>
    <p>BiRefNet 大模型 | 单张/批量处理 | 前后对比 | 自由换背景</p>
</div>
""", unsafe_allow_html=True)

# 背景颜色选择
col_bg1, col_bg2 = st.columns([1, 3])
with col_bg1:
    st.write("**背景颜色**")
with col_bg2:
    bg_options = {
        "transparent": "✨ 透明",
        "#FFFFFF": "⬜ 白色",
        "#000000": "⬛ 黑色",
        "#ef4444": "🟥 红色",
        "#22c55e": "🟩 绿色",
        "#3b82f6": "🟦 蓝色",
        "#f59e0b": "🟨 黄色",
    }
    bg_color = st.selectbox("选择背景", list(bg_options.keys()),
                            format_func=lambda x: bg_options[x], label_visibility="collapsed")

    if bg_color == "custom":
        bg_color = st.color_picker("自定义颜色", "#f59e0b")

    custom_color = st.checkbox("自定义颜色")
    if custom_color:
        bg_color = st.color_picker("选择颜色", "#f59e0b")

# 分隔线
st.markdown("---")

# ========== 单张处理 ==========
st.subheader("📤 单张抠图")

uploaded = st.file_uploader("上传图片", type=["png", "jpg", "jpeg", "webp", "bmp"],
                           label_visibility="collapsed")

if uploaded is not None:
    # 读取原图
    orig_img = Image.open(uploaded).convert("RGBA")

    # 处理按钮
    if st.button("🚀 开始抠图", type="primary"):
        with st.spinner("BiRefNet 模型处理中...首次加载需要1-2分钟"):
            result = remove_bg(orig_img)
            result_with_bg = apply_bg_color(result, bg_color)

        # 显示前后对比
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**原图**")
            st.image(orig_img, use_container_width=True)
        with col2:
            st.markdown("**抠图结果**")
            display_img = result_with_bg if bg_color != "transparent" else result
            st.image(display_img, use_container_width=True)

        # 下载按钮
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            buf = img_to_download(result_with_bg if bg_color != "transparent" else result, "PNG")
            st.download_button("📥 下载 PNG", buf, file_name=f"cutout_{uploaded.name.rsplit('.',1)[0]}.png",
                             mime="image/png")
        with dl_col2:
            buf_jpg = img_to_download(result, "JPEG")
            st.download_button("📥 下载 JPG(白底)", buf_jpg,
                             file_name=f"cutout_{uploaded.name.rsplit('.',1)[0]}.jpg",
                             mime="image/jpeg")

# ========== 批量处理 ==========
st.markdown("---")
st.subheader("📦 批量抠图")

batch_files = st.file_uploader("批量上传图片（最多50张）",
                              type=["png", "jpg", "jpeg", "webp", "bmp"],
                              accept_multiple_files=True,
                              label_visibility="collapsed")

if batch_files and len(batch_files) > 0:
    st.info(f"已上传 {len(batch_files)} 张图片")

    if st.button(f"🚀 批量处理 {len(batch_files)} 张图片", type="primary"):
        progress = st.progress(0)
        results = []

        for i, f in enumerate(batch_files):
            with st.spinner(f"处理中... {i+1}/{len(batch_files)}"):
                try:
                    img = Image.open(f).convert("RGBA")
                    out = remove_bg(img)
                    out_with_bg = apply_bg_color(out, bg_color)
                    results.append({
                        "name": f.name,
                        "orig": img,
                        "result": out,
                        "result_bg": out_with_bg,
                    })
                except Exception as e:
                    st.error(f"{f.name} 处理失败: {e}")
            progress.progress((i + 1) / len(batch_files))

        # 显示结果网格
        st.success(f"✅ 处理完成！{len(results)} 张图片")

        cols_per_row = 3
        for i in range(0, len(results), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(results):
                    r = results[i + j]
                    with col:
                        st.caption(r["name"])
                        display = r["result_bg"] if bg_color != "transparent" else r["result"]
                        st.image(display, use_container_width=True)

        # 打包ZIP下载
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for r in results:
                img_buf = io.BytesIO()
                r["result"].save(img_buf, format="PNG")
                zf.writestr(f"{r['name'].rsplit('.',1)[0]}_cutout.png", img_buf.getvalue())

        zip_buf.seek(0)
        st.download_button("📥 下载全部 (ZIP)", zip_buf,
                         file_name="batch_cutouts.zip",
                         mime="application/zip")

# ========== 底部信息 ==========
st.markdown("---")
st.caption("🔧 Powered by BiRefNet + rembg | PixelCraft AI 智能抠图")
