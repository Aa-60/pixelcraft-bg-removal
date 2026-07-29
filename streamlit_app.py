# -*- coding: utf-8 -*-
"""PixelCraft - AI 智能抠图"""
import io
import zipfile
from datetime import datetime

import streamlit as st
from PIL import Image
from rembg import remove

st.set_page_config(page_title="PixelCraft", page_icon="✂️", layout="centered")

st.title("PixelCraft")
st.write("AI 驱动的智能抠图工具")

# 侧边栏设置
with st.sidebar:
    st.header("设置")
    bg_color = st.selectbox(
        "背景颜色",
        ["透明", "白色", "黑色", "红色", "绿色", "蓝色"],
        index=0,
    )
    output_format = st.selectbox("输出格式", ["PNG", "JPG", "WEBP"], index=0)

# 背景色映射
BG_MAP = {
    "透明": None,
    "白色": "#FFFFFF",
    "黑色": "#000000",
    "红色": "#EF4444",
    "绿色": "#22C55E",
    "蓝色": "#3B82F6",
}


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def process_image(img, bg_name):
    """抠图并应用背景"""
    out = remove(img)
    if out.mode != "RGBA":
        out = out.convert("RGBA")
    bg_hex = BG_MAP.get(bg_name)
    if bg_hex:
        bg_rgb = hex_to_rgb(bg_hex)
        new_bg = Image.new("RGBA", out.size, bg_rgb + (255,))
        out = Image.alpha_composite(new_bg, out)
    return out


def save_to_buf(img, fmt):
    buf = io.BytesIO()
    if fmt == "JPG":
        img.convert("RGB").save(buf, format="JPEG", quality=95)
        return buf, "image/jpeg", "jpg"
    elif fmt == "WEBP":
        img.save(buf, format="WEBP", quality=95)
        return buf, "image/webp", "webp"
    else:
        img.save(buf, format="PNG")
        return buf, "image/png", "png"


# 单张处理
tab1, tab2 = st.tabs(["单张处理", "批量处理"])

with tab1:
    f = st.file_uploader("上传图片", type=["png", "jpg", "jpeg", "webp", "bmp"])
    if f:
        img = Image.open(f).convert("RGBA")
        c1, c2 = st.columns(2)
        with c1:
            st.write("原图")
            st.image(img, use_container_width=True)
        with c2:
            st.write("抠图结果")
            with st.spinner("AI 处理中..."):
                result = process_image(img, bg_color)
            st.image(result, use_container_width=True)
            buf, mime, ext = save_to_buf(result, output_format)
            st.download_button("下载", buf, file_name=f"cutout.{ext}", mime=mime)

with tab2:
    files = st.file_uploader("批量上传", type=["png", "jpg", "jpeg", "webp", "bmp"], accept_multiple_files=True)
    if files:
        st.write(f"已选 {len(files)} 张")
        if st.button("开始批量抠图"):
            progress = st.progress(0)
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, f in enumerate(files):
                    progress.progress((i + 1) / len(files))
                    try:
                        img = Image.open(f).convert("RGBA")
                        result = process_image(img, bg_color)
                        b = io.BytesIO()
                        result.save(b, format="PNG")
                        zf.writestr(f"{f.name.rsplit('.', 1)[0]}_cutout.png", b.getvalue())
                    except Exception as e:
                        st.error(f"{f.name} 失败: {e}")
            progress.empty()
            zip_buf.seek(0)
            st.download_button(
                "下载全部 (ZIP)",
                zip_buf,
                file_name=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
            )

st.write("---")
st.caption("Powered by rembg | PixelCraft")
