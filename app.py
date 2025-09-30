import os, io, zipfile
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

st.set_page_config(page_title="BulkEdit — Batch Image Editor", page_icon="🖼️", layout="wide")
st.title("🖼️ BulkEdit — Batch Image Crop/Resize/Watermark")
st.caption("Upload images → choose size & optional watermark → download ZIP. No external API needed.")

files = st.file_uploader("Upload images", type=["jpg","jpeg","png"], accept_multiple_files=True)

col1, col2 = st.columns(2)
with col1:
    width  = st.number_input("Width", 256, 4096, 1080)
    height = st.number_input("Height", 256, 4096, 1080)
    keep_aspect = st.checkbox("Keep aspect ratio (pad to fit)", value=False)
with col2:
    wm_text = st.text_input("Watermark text (optional)", "")
    wm_size = st.slider("Watermark font size", 12, 96, 28)
    wm_margin = st.slider("Watermark bottom margin (px)", 0, 200, 20)

def resize_image(im: Image.Image, W: int, H: int, keep: bool) -> Image.Image:
    if not keep:
        return im.resize((W, H))
    im = im.convert("RGB")
    im_ratio = im.width / im.height
    target_ratio = W / H
    if im_ratio > target_ratio:
        new_w = W; new_h = int(W / im_ratio)
    else:
        new_h = H; new_w = int(H * im_ratio)
    ims = im.resize((new_w, new_h))
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    x = (W - new_w) // 2; y = (H - new_h) // 2
    canvas.paste(ims, (x, y))
    return canvas

def apply_watermark(im: Image.Image, text: str, size: int, margin: int) -> Image.Image:
    if not text.strip(): return im
    im = im.copy()
    draw = ImageDraw.Draw(im)
    try: font = ImageFont.truetype("arial.ttf", size)
    except: 
        from PIL import ImageFont as F
        font = F.load_default()
    W, H = im.size
    tw, th = draw.textbbox((0,0), text, font=font)[2:]
    x = 10; y = H - th - margin
    draw.text((x, y), text, fill=(255,255,255), font=font, stroke_width=2, stroke_fill=(0,0,0))
    return im

if st.button("▶️ Process Images", type="primary", use_container_width=True):
    if not files:
        st.error("Please upload at least one image."); st.stop()
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            im = Image.open(f).convert("RGB")
            im = resize_image(im, int(width), int(height), keep_aspect)
            im = apply_watermark(im, wm_text, wm_size, wm_margin)
            buf = io.BytesIO(); im.save(buf, format="JPEG", quality=92); buf.seek(0)
            base = os.path.splitext(f.name)[0]
            z.writestr(f"{base}_edited.jpg", buf.read())
    mem.seek(0)
    st.success(f"Processed {len(files)} image(s).")
    st.download_button("⬇️ Download ZIP", mem.getvalue(), "edited_images.zip", "application/zip")

st.markdown("---")
st.caption("Tip: ‘Keep aspect ratio’ ON se white padding add hotta hai; OFF se exact resize/crop hotta hai.")
