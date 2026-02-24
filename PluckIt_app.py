import streamlit as st
import yt_dlp
import os
import re

# --- Page Configuration ---
st.set_page_config(page_title="Pluck It Pro", page_icon="📥", layout="wide")

# Custom CSS to make it look professional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📥 Pluck It Pro")
st.markdown("---")

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
    st.header("⚙️ Settings")
    mode = st.radio("Download Mode", ["Video (MP4)", "Audio (MP3)"])
    if mode == "Video (MP4)":
        quality_label = st.selectbox("Resolution", list(v_options.keys()), index=1)
        selected_quality = v_options[quality_label]
    else:
        quality_label = st.selectbox("Bitrate", list(a_options.keys()), index=2)
        selected_quality = a_options[quality_label]
    
    saved_val, unit = get_savings(mode, quality_label)
    if saved_val > 0:
        st.metric("Storage Saved", f"{saved_val} {unit}", help="Estimated vs. highest quality option")
    
    st.info("💡 Tip: If you get a 403 error, try updating yt-dlp via 'pip install -U yt-dlp'.")

# --- Main Interface ---
url = st.text_input("Enter URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    with st.expander("📺 Preview Video Snippet", expanded=True):
        try:
            st.video(url)
        except:
            st.warning("Preview not available for this link.")

    # 1. Base YDL Options to bypass 403 Forbidden
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        # Bypass 403: Use modern headers and mimic different clients
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }

    # 2. Add Cookies (Optional but Recommended)
    # If cookies.txt exists in your folder, yt-dlp will use it automatically
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    # 3. Format Selection Logic
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
        # Create downloads folder if not exists
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        progress_bar = st.progress(0)
        status = st.empty()
        
        def hook(d):
            if d['status'] == 'downloading':
                # Remove % and get numeric value for progress bar
                p_str = d.get('_percent_str', '0%')
                p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_str).replace('%','') # Clean ANSI codes
                try:
                    progress_bar.progress(float(p_clean)/100)
                    status.text(f"Plucking... {p_str}")
                except:
                    pass
            if d['status'] == 'finished':
                status.text("Processing complete. Ready for download!")

        ydl_opts['progress_hooks'] = [hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
                # Correction for audio extension after post-processing
                if mode == "Audio (MP3)":
                    file_path = os.path.splitext(file_path)[0] + ".mp3"

            # 4. Final Download Button
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"💾 Save {mode} to Device", 
                    data=f, 
                    file_name=os.path.basename(file_path),
                    mime="video/mp4" if mode == "Video (MP4)" else "audio/mpeg"
                )
            
            # 5. Clean up server storage
            os.remove(file_path)
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("If the error persists, YouTube might be blocking this IP. Try running the app locally with a 'cookies.txt' file.")
