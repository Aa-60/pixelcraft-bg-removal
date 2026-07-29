# -*- coding: utf-8 -*-
"""
PixelCraft - Streamlit Cloud 版本
AI 智能抠图工具
"""
import os
import io
import zipfile
from datetime import datetime

os.environ["ONNXRUNTIME_EXECUTION_PROVIDERS"] = "CPUExecutionProvider"

import streamlit as st
import numpy as np
from PIL import Image
from rembg import remove, new_session

# Page config
st.set_page_config(
    page_title="PixelCraft - AI 智能抠图",
    page_icon="✂️",
    layout="centered",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white !important;
        font-weight: 900 !important;
        margin: 0 !important;
    }
    .main-header p {
        color: rgba(255,255,255,0.85) !important;
        margin: 0.5rem 0 0 0 !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
    }
    .stButton>button:hover {
        opacity: 0.9;
    }
    .download-btn {
        background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>PixelCraft</h1>
    <p>AI 驱动的智能抠图工具 | 批量处理 | 自由换背景 | 一键下载</p>
</div>
""", unsafe_allow_html=True)

# Cache model session
@st.cache_resource
def get_session():
    st.info("首次加载 BiRefNet 模型，请稍候...")
    return new_session(model_name="birefnet-general")


def remove_bg(img):
    """Remove background using BiRefNet."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    session = get_session()
    out = remove(img, session=session)
    if out.mode != "RGBA":
        out = out.convert("RGBA")
    return out


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# Sidebar settings
with st.sidebar:
    st.header("⚙️ 设置")

    bg_color = st.selectbox(
        "背景颜色",
        options=[
            ("transparent", "透明"),
            ("#FFFFFF", "白色"),
            ("#000000", "黑色"),
            ("#EF4444", "红色"),
            ("#22C55E", "绿色"),
            ("#3B82F6", "蓝色"),
            ("#F59E0B", "黄色"),
            ("#EC4899", "粉色"),
        ],
        format_func=lambda x: x[1],
    )[0]

    output_format = st.selectbox(
        "输出格式",
        options=["PNG", "JPEG", "WEBP"],
        index=0,
    )

    st.markdown("---")
    st.markdown("**关于**")
    st.markdown("基于 BiRefNet 大模型 | 永久免费在线")


# Main area tabs
tab_single, tab_batch = st.tabs(["📷 单张处理", "📁 批量处理"])

# Single image tab
with tab_single:
    uploaded_file = st.file_uploader(
        "上传图片",
        type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
        help="支持 PNG / JPG / WEBP / BMP / TIFF",
    )

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGBA")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("原图")
            st.image(img, use_container_width=True)

        with col2:
            st.subheader("抠图结果")
            with st.spinner("AI 正在抠图..."):
                removed = remove_bg(img)

                if bg_color != "transparent":
                    bg_rgb = hex_to_rgb(bg_color)
                    new_bg = Image.new("RGBA", removed.size, bg_rgb + (255,))
                    result = Image.alpha_composite(new_bg, removed)
                    if output_format == "JPEG":
                        result = result.convert("RGB")
                else:
                    result = removed

            st.image(result, use_container_width=True)

            # Download
            buf = io.BytesIO()
            if output_format == "JPEG":
                result.convert("RGB").save(buf, format="JPEG", quality=95)
                mime = "image/jpeg"
                ext = "jpg"
            elif output_format == "WEBP":
                result.save(buf, format="WEBP", quality=95)
                mime = "image/webp"
                ext = "webp"
            else:
                result.save(buf, format="PNG")
                mime = "image/png"
                ext = "png"
            buf.seek(0)

            st.download_button(
                label="⬇️ 下载结果",
                data=buf,
                file_name=f"pixelcraft_{uploaded_file.name.rsplit('.', 1)[0]}_cutout.{ext}",
                mime=mime,
                use_container_width=True,
            )


# Batch tab
with tab_batch:
    uploaded_files = st.file_uploader(
        "批量上传图片（支持拖拽多张）",
        type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
        accept_multiple_files=True,
        help="一次最多处理 100 张",
    )

    if uploaded_files:
        st.write(f"已选择 **{len(uploaded_files)}** 张图片")

        if st.button("🚀 开始批量抠图", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()

            zip_buf = io.BytesIO()
            results = []

            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, f in enumerate(uploaded_files):
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    status_text.text(f"处理第 {i+1}/{len(uploaded_files)} 张: {f.name}")

                    try:
                        img = Image.open(f).convert("RGBA")
                        removed = remove_bg(img)

                        if bg_color != "transparent":
                            bg_rgb = hex_to_rgb(bg_color)
                            new_bg = Image.new("RGBA", removed.size, bg_rgb + (255,))
                            result = Image.alpha_composite(new_bg, removed).convert("RGB")
                        else:
                            result = removed

                        # Save to zip
                        out_buf = io.BytesIO()
                        if bg_color != "transparent":
                            result.save(out_buf, format="PNG", quality=95)
                        else:
                            result.save(out_buf, format="PNG")
                        out_buf.seek(0)
                        fname = f"{f.name.rsplit('.', 1)[0]}_cutout.png"
                        zf.writestr(fname, out_buf.getvalue())

                        results.append({
                            "filename": f.name,
                            "status": "✅ 成功",
                            "preview": result,
                        })
                    except Exception as e:
                        results.append({
                            "filename": f.name,
                            "status": f"❌ 失败: {str(e)[:50]}",
                        })

            progress_bar.empty()
            status_text.empty()

            # Show results
            st.success(f"完成！成功 {sum(1 for r in results if '✅' in r['status'])}/{len(uploaded_files)} 张")

            # Show previews (first 6)
            previews = [r for r in results if "preview" in r][:6]
            if previews:
                cols = st.columns(min(3, len(previews)))
                for idx, item in enumerate(previews):
                    with cols[idx % 3]:
                        st.image(item["preview"], caption=item["filename"], use_container_width=True)

            # Download zip
            zip_buf.seek(0)
            st.download_button(
                label="⬇️ 下载全部 (ZIP)",
                data=zip_buf,
                file_name=f"pixelcraft_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True,
            )

            # Show summary table
            with st.expander("查看处理详情"):
                for r in results:
                    st.write(f"{r['status']} - {r['filename']}")


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#94a3b8;font-size:.8rem'>"
    "Powered by BiRefNet | PixelCraft | 永久免费在线"
    "</div>",
    unsafe_allow_html=True,
)
