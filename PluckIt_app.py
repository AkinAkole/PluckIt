import streamlit as st
import yt_dlp
import os
import re
import tempfile

# --- Page Configuration ---
st.set_page_config(page_title="Pluck It Pro", page_icon="📥", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #FF0000; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📥 Pluck It Pro")
st.caption("2026 PoX (Proof of Existence) & PO-Token Bypass Edition")

# --- Sidebar: Configuration ---
v_options = {"1080p": "1080", "720p": "720", "480p": "480", "360p": "360", "240p": "240"}
a_options = {"320 kbps": "320", "256 kbps": "256", "192 kbps": "192", "128 kbps": "128", "96 kbps": "96", "64 kbps": "64"}

with st.sidebar:
    st.header("⚙️ Pluck Settings")
    mode = st.radio("Output Type", ["Video (MP4)", "Audio (MP3)"])
    if mode == "Video (MP4)":
        quality_label = st.selectbox("Max Resolution", list(v_options.keys()), index=1)
        selected_quality = v_options[quality_label]
    else:
        quality_label = st.selectbox("Audio Bitrate", list(a_options.keys()), index=2)
        selected_quality = a_options[quality_label]
    
    st.info("💡 If you still get a 403, ensure your 'cookies.txt' is fresh and was exported from an Incognito tab.")

# --- Main Interface ---
url = st.text_input("YouTube URL:", placeholder="Paste link here...")

if url:
    with st.expander("📺 Preview", expanded=False):
        try:
            st.video(url)
        except:
            st.info("Preview restricted by YouTube, but download may still work.")

    # --- THE PoX & PO-TOKEN BYPASS CONFIG ---
    # This configuration targets clients that currently have the lowest PO-Token enforcement
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'source_address': '0.0.0.0', # Force IPv4
        'nocheckcertificate': True,
        
        # 1. PoX STRATEGY: Use specific trusted clients & skip standard webpage extraction
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'tv', 'mweb'],
                'player_skip': ['webpage', 'configs'],
                # Add a manual PO Token if you have one (optional)
                # 'po_token': 'mweb.gvs+YOUR_TOKEN_HERE' 
            }
        },
        
        # 2. DISABLE MANIFESTS: Prevents the initial 403 trigger on manifest fetching
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
        
        # 3. STEALTH HEADERS
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
        },
    }

    # --- Handle Cookies (Critical for PoX) ---
    if "YT_COOKIES" in st.secrets:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            tmp.write(st.secrets["YT_COOKIES"])
            ydl_opts['cookiefile'] = tmp.name
    elif os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    # Format Logic
    if mode == "Video (MP4)":
        ydl_opts['format'] = f'bestvideo[height<={selected_quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={selected_quality}][ext=mp4]'
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': selected_quality,
        }]

    if st.button("🚀 Pluck Now"):
        if not os.path.exists("downloads"): os.makedirs("downloads")
        
        progress_bar = st.progress(0)
        status = st.empty()
        
        def hook(d):
            if d['status'] == 'downloading':
                p_str = d.get('_percent_str', '0%')
                p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_str).replace('%','')
                try:
                    progress_bar.progress(float(p_clean)/100)
                    status.text(f"Processing... {p_str}")
                except: pass

        ydl_opts['progress_hooks'] = [hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
                if mode == "Audio (MP3)":
                    file_path = os.path.splitext(file_path)[0] + ".mp3"

            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"💾 Save {mode}",
                    data=f,
                    file_name=os.path.basename(file_path),
                    mime="video/mp4" if mode == "Video (MP4)" else "audio/mpeg"
                )
            os.remove(file_path)
            st.success("Pluck Complete!")
            
        except Exception as e:
            st.error(f"403 Blocked: {e}")
            st.write("YouTube detected automation. Ensure you are using 'ios' as the primary client in the code.")
