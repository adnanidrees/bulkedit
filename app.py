import os, io, json, time
import streamlit as st

# ---- Bridge Streamlit Secrets → ENV ----
try:
    os.environ.setdefault("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY",""))
except Exception:
    pass

st.set_page_config(page_title="BulkEdit", page_icon="🖼️", layout="wide")
st.title("🖼️ BulkEdit")
st.caption("Batch image crop/resize/watermark")

st.write('This is a placeholder app body.')