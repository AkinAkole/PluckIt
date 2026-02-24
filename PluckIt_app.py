import streamlit as st
import yt_dlp
import os
import re
import tempfile

# --- Page Configuration ---
st.set_page_config(page_title="Pluck It Pro", page_icon="📥", layout="wide")

st.title("📥 Pluck It Pro")
st.caption("2026 PO-Token & Integrity Bypass")

# Input for Tokens (This avoids hardcoding personal tokens)
with st.expander("🔑 2026 Security Bypass (Required for Cloud)"):
    po_token = st.text_input("Enter PO Token:", help="Found in F12 -> Network -> v1/player -> poToken")
    visitor_data = st.text_input("Enter Visitor Data:", help="Found in F12 -> Network -> v1/player -> visitorData")

url = st.text_input("YouTube URL:", placeholder="Paste link here...")

if url:
    # --- CONSOLIDATED ULTIMATE BYPASS CONFIG ---
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'source_address': '0.0.0.0', 
        
        # 1. PoX & Integrity Strategy
        'extractor_args': {
            'youtube': {
                # We use mweb because it's currently the most 'human-like' for tokens
                'player_client': ['mweb', 'ios'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        
        # 2. Injecting your specific session tokens
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
        'nocheckcertificate': True,
    }

    # Inject Tokens if provided
    if po_token and visitor_data:
        ydl_opts['extractor_args']['youtube']['po_token'] = f'mweb.gvs+{po_token}'
        ydl_opts['extractor_args']['youtube']['visitor_data'] = visitor_data

    # 3. Cookie Handling (From Secrets or Local)
    if "YT_COOKIES" in st.secrets:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            tmp.write(st.secrets["YT_COOKIES"])
            ydl_opts['cookiefile'] = tmp.name
    elif os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    if st.button("🚀 Pluck Now"):
        if not os.path.exists("downloads"): os.makedirs("downloads")
        
        # Simple progress bar
        p_bar = st.progress(0)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            with open(file_path, "rb") as f:
                st.download_button("💾 Save File", f, file_name=os.path.basename(file_path))
            
            os.remove(file_path)
            st.success("Download Ready!")
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.warning("If 403 persists, your PO Token or Cookies may have expired. Refresh them in an Incognito tab.")
