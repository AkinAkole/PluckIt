import streamlit as st
import yt_dlp
import os

# --- Page Configuration ---
st.set_page_config(page_title="Pluck It Pro", page_icon="📥", layout="wide")

st.title("📥 Pluck It Pro")

# Helper to calculate estimated savings
def get_savings(mode, quality_key):
    # Estimated MB per minute
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
    st.header("⚙️ Settings")
    mode = st.radio("Download Mode", ["Video (MP4)", "Audio (MP3)"])
    if mode == "Video (MP4)":
        quality_label = st.selectbox("Resolution", list(v_options.keys()), index=1)
        selected_quality = v_options[quality_label]
    else:
        quality_label = st.selectbox("Bitrate", list(a_options.keys()), index=2)
        selected_quality = a_options[quality_label]
    
    # Data Savings Calculator
    saved_val, unit = get_savings(mode, quality_label)
    if saved_val > 0:
        st.metric("Storage Saved", f"{saved_val} {unit}", help="Estimated vs. highest quality option")

# --- Main Interface ---
url = st.text_input("Enter URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    # 1. Video Preview Feature
    with st.expander("📺 Preview Video Snippet", expanded=True):
        try:
            st.video(url)
        except:
            st.warning("Preview not available for this link.")

    # 2. Download Logic
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
            'Referer': 'https://www.google.com/',
        },
    }

    if mode == "Video (MP4)":
        ydl_opts['format'] = f'bestvideo[height<={selected_quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={selected_quality}]'
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': selected_quality,
        }]

    if st.button("🚀 Pluck Now"):
        progress_bar = st.progress(0)
        status = st.empty()
        
        def hook(d):
            if d['status'] == 'downloading':
                p = d.get('_percent_str', '0%').replace('%','')
                progress_bar.progress(float(p)/100)
                status.text(f"Plucking... {d.get('_percent_str')}")

        ydl_opts['progress_hooks'] = [hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if mode == "Audio (MP3)":
                    file_path = os.path.splitext(file_path)[0] + ".mp3"

            with open(file_path, "rb") as f:
                st.download_button(f"💾 Download {quality_label}", f, file_name=os.path.basename(file_path))
            os.remove(file_path)
        except Exception as e:
            st.error(f"Error: {e}")
