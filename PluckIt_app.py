import streamlit as st
import yt_dlp
import os

# --- Page Configuration ---
st.set_page_config(page_title="Pluck It Pro", page_icon="📥", layout="centered")

st.title("📥 Pluck It Pro")

# Ensure download directory exists
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- Progress Hook Function ---
def progress_hook(d):
    if d['status'] == 'downloading':
        # Extract percentage from the yt-dlp dictionary
        p = d.get('_percent_str', '0%').replace('%','')
        try:
            progress_float = float(p) / 100
            progress_bar.progress(progress_float)
            status_text.text(f"Downloading: {d.get('_percent_str')} at {d.get('_speed_str')}")
        except:
            pass
    if d['status'] == 'finished':
        status_text.text("Download complete! Converting...")

# --- Sidebar: Quality Configuration ---
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

# --- Main Input ---
url = st.text_input("Paste Media URL:", placeholder="YouTube, Facebook, SoundCloud...")

if url:
    # Build yt-dlp options
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'noplaylist': True,
        'progress_hooks': [progress_hook], # Connect the progress bar
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
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

    if st.button("Pluck It"):
        # Create UI placeholders for the progress
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
                if mode == "Audio (MP3)":
                    file_path = os.path.splitext(file_path)[0] + ".mp3"

            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    st.success(f"✅ Ready: {info.get('title')}")
                    st.download_button(
                        label=f"💾 Download {mode}",
                        data=f,
                        file_name=os.path.basename(file_path),
                        mime="video/mp4" if mode == "Video (MP4)" else "audio/mpeg"
                    )
                os.remove(file_path) # Clean up
        
        except Exception as e:
            st.error(f"Failed to pluck media: {e}")

st.markdown("---")
st.caption("Pluck It Pro | Status: Operational")
