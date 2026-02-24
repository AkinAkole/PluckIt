import streamlit as st
import yt_dlp
import os

# --- Page Configuration ---
st.set_page_config(page_title="Pluck It", page_icon="📥")

st.title("📥 Pluck It")
st.markdown("If you get a **403 error**, the site is blocking the cloud server's IP. Try a different link or use a Private repo with cookies.")

# Ensure a download folder exists
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- UI Layout ---
with st.sidebar:
    st.header("Settings")
    file_format = st.selectbox("Select Format", ["mp4", "mp3"])
    quality = st.select_slider("Quality Profile", options=["worst", "best"], value="best")

url = st.text_input("Enter Media URL:", placeholder="https://...")

if url:
    # 1. Advanced Options to bypass 403 Forbidden
    ydl_opts = {
        # Format selection
        'format': f'{quality}[ext={file_format}]/best' if file_format == 'mp4' else 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'noplaylist': True,
        
        # Browser Impersonation (The "Anti-403" Suite)
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        },
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': False,
    }

    # Optional: Load cookies if you have them in your repo (Private Repo ONLY)
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'

    # 2. Audio Conversion Logic
    if file_format == "mp3":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    if st.button("Pluck It"):
        try:
            with st.spinner("Plucking... Please wait."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Download the file
                    info = ydl.extract_info(url, download=True)
                    raw_path = ydl.prepare_filename(info)
                    
                    # Ensure extension is correct after post-processing
                    if file_format == "mp3":
                        final_path = os.path.splitext(raw_path)[0] + ".mp3"
                    else:
                        final_path = raw_path

                # 3. Serve the file to the user
                if os.path.exists(final_path):
                    with open(final_path, "rb") as f:
                        st.success(f"Successfully Plucked: {info.get('title')}")
                        st.download_button(
                            label="⬇️ Download Now",
                            data=f,
                            file_name=os.path.basename(final_path),
                            mime="video/mp4" if file_format == "mp4" else "audio/mpeg"
                        )
                    # Cleanup: remove file from server after it's ready for download
                    os.remove(final_path)

        except Exception as e:
            st.error(f"Plucking failed. ERROR: {e}")
            if "403" in str(e):
                st.warning("💡 **Pro-Tip:** Streamlit's servers are often blocked by YouTube. If this fails, try a SoundCloud or Facebook link to confirm the app works.")
