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
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("📥 Pluck It Pro")
st.caption("Ultimate 2026 Bypass Edition - Powered by PoX & iOS Client Spoofing")

# Helper to calculate estimated savings
def get_savings(mode, quality_key):
    video_sizes = {"1080p": 120, "720p": 60, "480p": 30, "360p": 15, "240p": 8}
    audio_sizes = {"320 kbps": 2.4, "256 kbps": 1.9, "192 kbps": 1.4, "128 kbps": 1.0, "96 kbps": 0.7, "64 kbps": 0.5}
    if mode == "Video (MP4)":
        saved = video_sizes["1080p"] - video_sizes.get(quality_key, 120)
        return saved, "MB/min"
    else:
        saved = audio_sizes["320 kbps"] - audio_sizes.get(quality_key, 2.4)
        return round(saved, 1), "MB/min"

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
    
    st.markdown("---")
    saved_val, unit = get_savings(mode, quality_label)
    if saved_val > 0:
        st.metric("Efficiency Gain", f"{saved_val} {unit}")

# --- Main Interface ---
url = st.text_input("YouTube URL:", placeholder="Paste link here...")

if url:
    with st.expander("📺 Preview", expanded=False):
        try:
            st.video(url)
        except:
            st.info("Direct preview not available, but plucking should still work.")

    # --- THE ULTIMATE 2026 BYPASS CONFIG ---
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        # 1. Force IPv4 (Streamlit Cloud IPs are often blocked on IPv6)
        'source_address': '0.0.0.0',
        # 2. PoX & Client Bypass (iOS and TV clients are the most trusted in 2026)
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'tv'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        # 3. Modern Headers
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        # 4. Disable DASH/HLS manifests which often trigger 403 checks
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
        'nocheckcertificate': True,
    }

    # --- Cookie Logic (Bypasses blacklisted server IPs) ---
    if "YT_COOKIES" in st.secrets:
        # For Deployment: Use Streamlit Secrets
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            tmp.write(st.secrets["YT_COOKIES"])
            ydl_opts['cookiefile'] = tmp.name
    elif os.path.exists('cookies.txt'):
        # For Local: Use local file
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
                # Clean ANSI color codes from string
                p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_str).replace('%','')
                try:
                    progress_bar.progress(float(p_clean)/100)
                    status.text(f"Status: Plucking {p_str}...")
                except: pass
            if d['status'] == 'finished':
                status.text("Plucking complete! Finalizing file...")

        ydl_opts['progress_hooks'] = [hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
                # Update path if it was converted to MP3
                if mode == "Audio (MP3)":
                    file_path = os.path.splitext(file_path)[0] + ".mp3"

            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"💾 Download {quality_label} {mode}",
                    data=f,
                    file_name=os.path.basename(file_path),
                    mime="video/mp4" if mode == "Video (MP4)" else "audio/mpeg"
                )
            
            # Clean up server file immediately
            os.remove(file_path)
            st.success("Plucked successfully!")
            
        except Exception as e:
            st.error(f"Plucking Failed: {e}")
            st.info("Note: If you are on Streamlit Cloud, you MUST use 'cookies.txt' because YouTube blocks Cloud IPs.")
