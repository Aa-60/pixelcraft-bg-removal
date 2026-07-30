# -*- coding: utf-8 -*-
"""
PixelCraft - AI 智能抠图
Flask + BiRefNet 模型，支持单张/批量处理、前后对比、自由换背景
"""
import os
import sys
import io
import base64
import traceback
import socket
import zipfile

os.environ["U2NET_HOME"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.environ["ONNXRUNTIME_EXECUTION_PROVIDERS"] = "CPUExecutionProvider"

from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
from rembg import remove, new_session

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
)

SUPPORTED_FORMATS = {"PNG": "PNG", "JPG": "JPEG", "JPEG": "JPEG", "WEBP": "WEBP", "BMP": "BMP", "TIFF": "TIFF"}
EXT_MAP = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp", "BMP": ".bmp", "TIFF": ".tiff"}
MIME_MAP = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp", "BMP": "image/bmp", "TIFF": "image/tiff"}


def get_pil_format(fmt_str):
    return SUPPORTED_FORMATS.get(fmt_str.strip().upper(), "PNG")


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# Cache model session (load once, reuse)
_birefnet_session = None

def get_session():
    global _birefnet_session
    if _birefnet_session is None:
        print("Loading BiRefNet model (first time only)...")
        _birefnet_session = new_session(model_name="birefnet-general")
        print("BiRefNet model loaded!")
    return _birefnet_session


def remove_bg(input_bytes):
    """Remove background using BiRefNet. Return RGBA PIL Image."""
    img = Image.open(io.BytesIO(input_bytes)).convert("RGBA")
    out = remove(img, session=get_session())
    if out.mode != "RGBA":
        out = out.convert("RGBA")
    return out


def save_image(img, output_format):
    """Save PIL image to bytes buffer."""
    buf = io.BytesIO()
    if output_format == "JPEG":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        bg.save(buf, format="JPEG", quality=95)
    else:
        img.save(buf, format=output_format)
    buf.seek(0)
    return buf


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/remove-bg", methods=["POST"])
def api_remove_bg():
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"success": False, "error": "Please upload image"}), 400
        fmt = get_pil_format(request.form.get("output_format", "PNG"))
        out = remove_bg(file.read())
        buf = save_image(out, fmt)
        b64 = base64.b64encode(buf.read()).decode()
        mime = MIME_MAP.get(fmt, "image/png")
        return jsonify({"success": True, "image": f"data:{mime};base64,{b64}", "format": request.form.get("output_format", "PNG")})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/change-bg", methods=["POST"])
def api_change_bg():
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"success": False, "error": "Please upload image"}), 400
        fmt = get_pil_format(request.form.get("output_format", "PNG"))
        bg_color = request.form.get("bg_color", "#FFFFFF")
        removed = remove_bg(file.read())
        bg_rgb = hex_to_rgb(bg_color)
        new_bg = Image.new("RGBA", removed.size, bg_rgb + (255,))
        new_bg = Image.alpha_composite(new_bg, removed)
        buf = save_image(new_bg, fmt)
        b64 = base64.b64encode(buf.read()).decode()
        mime = MIME_MAP.get(fmt, "image/png")
        return jsonify({"success": True, "image": f"data:{mime};base64,{b64}", "format": request.form.get("output_format", "PNG"), "bg_color": bg_color})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/batch-remove-bg", methods=["POST"])
def api_batch_remove_bg():
    """Batch process images. ZIP contains transparent PNGs."""
    try:
        files = request.files.getlist("images")
        output_format = request.form.get("output_format", "PNG")
        results = []
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                try:
                    raw = f.read()
                    # Original thumbnail
                    orig = Image.open(io.BytesIO(raw)).convert("RGBA")
                    orig_thumb = orig.copy()
                    orig_thumb.thumbnail((300, 300), Image.LANCZOS)
                    ob = io.BytesIO()
                    orig_thumb.save(ob, format="PNG")
                    orig_b64 = base64.b64encode(ob.getvalue()).decode()

                    # Process
                    out = remove_bg(raw)
                    # Full-size transparent PNG for ZIP
                    fb = io.BytesIO()
                    out.save(fb, format="PNG")
                    zf.writestr(f"{os.path.splitext(f.filename)[0]}_cutout.png", fb.getvalue())

                    # Result thumbnail for grid display (300px)
                    res_thumb = out.copy()
                    res_thumb.thumbnail((300, 300), Image.LANCZOS)
                    rb = io.BytesIO()
                    res_thumb.save(rb, format="PNG")
                    res_b64 = base64.b64encode(rb.getvalue()).decode()

                    # Full-size result for modal/download
                    fb2 = io.BytesIO()
                    out.save(fb2, format="PNG")
                    res_full_b64 = base64.b64encode(fb2.getvalue()).decode()

                    results.append({
                        "filename": f.filename,
                        "orig": f"data:image/png;base64,{orig_b64}",
                        "result": f"data:image/png;base64,{res_b64}",
                        "result_full": f"data:image/png;base64,{res_full_b64}",
                        "status": "ok",
                    })
                except Exception as e:
                    results.append({"filename": f.filename, "status": "error", "error": str(e)})

        zip_buf.seek(0)
        zip_b64 = base64.b64encode(zip_buf.getvalue()).decode()
        preview = results[:10]
        return jsonify({
            "success": True,
            "total": len(files),
            "preview": preview,
            "zip_data": f"data:application/zip;base64,{zip_b64}",
            "output_format": output_format,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/download", methods=["POST"])
def api_download():
    try:
        data = request.json.get("image_data", "")
        fn = request.json.get("filename", "output.png")
        b64 = data.split(",")[1] if "," in data else data
        return send_file(io.BytesIO(base64.b64decode(b64)), as_attachment=True, download_name=fn)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    port = 5000
    host = "0.0.0.0"
    for a in sys.argv[1:]:
        if a.startswith("--port="): port = int(a.split("=")[1])
        elif a.startswith("--host="): host = a.split("=")[1]
    sep = "=" * 50
    print(f"\n{sep}")
    print("  PixelCraft - AI 智能抠图")
    print("  模型: BiRefNet | 批量处理 | 前后对比 | 自由换背景")
    print(sep)
    print(f"\n  Local:   http://localhost:{port}")
    print(f"  Network: http://{get_local_ip()}:{port}")
    print(f"\n  Press Ctrl+C to stop\n")
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
