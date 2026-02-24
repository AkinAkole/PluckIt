import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Pluck It", page_icon="🎵")

st.title("📥 Pluck It")
st.markdown("Paste a link below to 'pluck' your media from the web.")

# --- UI Sidebar / Options ---
with st.sidebar:
    st.header("Settings")
    file_format = st.selectbox("Select Format", ["mp4", "mp3"])
    quality = st.select_slider(
        "Quality Profile",
        options=["worst", "best"],
        value="best",
        help="Best provides highest resolution; worst saves data/time."
    )

# --- Main Input ---
url = st.text_input("Enter Media URL (YouTube, FB, SoundCloud, etc.):", placeholder="https://...")

if url:
    try:
        # Configuration for yt-dlp
        ydl_opts = {
            'format': f'{quality}[ext={file_format}]' if file_format == 'mp4' else 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
        }

        # Handle MP3 conversion
        if file_format == "mp3":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        if st.button("Prepare Download"):
            with st.spinner("Processing... this might take a second."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info)
                    
                    # yt-dlp might change extension for mp3
                    if file_format == "mp3":
                        file_path = os.path.splitext(file_path)[0] + ".mp3"

                with open(file_path, "rb") as f:
                    st.success(f"Ready!: {info.get('title')}")
                    st.download_button(
                        label=f"Click to Download {file_format.upper()}",
                        data=f,
                        file_name=os.path.basename(file_path),
                        mime=f"video/{file_format}" if file_format == "mp4" else "audio/mpeg"
                    )
    except Exception as e:
        st.error(f"An error occurred: {e}")