import streamlit as st
import yt_dlp
import os
import shutil

# Page Config
st.set_page_config(page_title="Pluck It", page_icon="📥", layout="centered")

# Custom CSS for a cleaner look
st.markdown("""
    <style>
    .main { text-align: center; }
    .stDownloadButton { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("📥 Pluck It")
st.subheader("Universal Media Downloader")

# Ensure the download directory exists
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("🔧 Settings")
    file_format = st.selectbox("Format", ["mp4", "mp3"])
    quality = st.select_slider(
        "Quality",
        options=["worst", "best"],
        value="best"
    )
    st.info("Note: MP3 conversion requires a few extra seconds.")

# --- Main Input ---
url = st.text_input("Paste URL here:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    # 1. Define yt-dlp Options to bypass 403 Forbidden
ydl_opts = {
        'format': f'{quality}[ext={file_format}]/best' if file_format == 'mp4' else 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'noplaylist': True,
        # Enhanced bypass headers
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        },
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': False, # Set to False temporarily to see more errors in logs
        'no_warnings': False,
    }
    # 2. Add Post-Processor for MP3
    if file_format == "mp3":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    if st.button("Pluck Media"):
        try:
            with st.spinner("Extracting media..."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Extract info first
                    info = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info)
                    
                    # Fix extension if it changed during post-processing (e.g. to .mp3)
                    if file_format == "mp3" and not file_path.endswith(".mp3"):
                        file_path = os.path.splitext(file_path)[0] + ".mp3"

                # Check if file exists before offering download
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        btn = st.download_button(
                            label=f"💾 Download {os.path.basename(file_path)}",
                            data=f,
                            file_name=os.path.basename(file_path),
                            mime="video/mp4" if file_format == "mp4" else "audio/mpeg"
                        )
                    
                    st.success("Plucking successful!")
                    
                    # 3. Cleanup: Remove the file from the server after showing the button
                    # In a real app, you might want to delay this or use a background task
                    # but for Streamlit Cloud, it's good practice.
                    
        except Exception as e:
            st.error(f"Plucking failed. {str(e)}")
            if "403" in str(e):
                st.warning("⚠️ The site is blocking this request. Try a different link or check if the video is private.")

# Footer
st.markdown("---")
st.caption("Pluck It | Built with Streamlit & yt-dlp")

