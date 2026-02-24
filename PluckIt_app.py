import streamlit as st
import yt_dlp
import os
import re
import tempfile

st.set_page_config(page_title="Pluck It Pro", page_icon="📥")

st.title("📥 Pluck It Pro: 2026 Integrity Bypass")

# 1. Token Input (Critical for Cloud Deployments)
with st.expander("🔑 Mandatory 2026 Security Bypass"):
    st.write("YouTube blocks Cloud IPs. You must provide a PO Token from your browser.")
    po_token = st.text_input("PO Token", placeholder="Starts with 'mweb.gvs' or similar...")
    visitor_data = st.text_input("Visitor Data", placeholder="Usually a long base64 string...")

url = st.text_input("Enter URL:")

if url:
    # --- CONSOLIDATED BYPASS OPTIONS ---
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'source_address': '0.0.0.0', # Force IPv4
        'nocheckcertificate': True,
        
        # 2. CLIENT ROTATION (PoX Strategy)
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'ios', 'tv'], # Rotate through trusted clients
                'player_skip': ['webpage', 'configs'],
            }
        },
        
        # 3. DISABLE MANIFESTS (Avoids 403 on startup)
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
    }

    # 4. INJECT TOKENS (This 'vouches' for the bot)
    if po_token and visitor_data:
        # Note: If your token starts with mweb, ensure prefix is correct
        token_prefix = "mweb.gvs+" if not po_token.startswith("mweb") else ""
        ydl_opts['extractor_args']['youtube']['po_token'] = f"{token_prefix}{po_token}"
        ydl_opts['extractor_args']['youtube']['visitor_data'] = visitor_data

    # 5. COOKIE HANDLING
    if "YT_COOKIES" in st.secrets:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            tmp.write(st.secrets["YT_COOKIES"])
            ydl_opts['cookiefile'] = tmp.name
    elif os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    if st.button("🚀 Pluck Now"):
        if not po_token or not visitor_data:
            st.warning("⚠️ Warning: Skipping tokens may result in a 403 error on Cloud servers.")
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
            with open(file_path, "rb") as f:
                st.download_button("💾 Download File", f, file_name=os.path.basename(file_path))
            os.remove(file_path)
            st.success("Download Complete!")
            
        except Exception as e:
            st.error(f"YouTube Blocked the Request: {e}")
            st.info("Try refreshing your PO Token in an Incognito tab.")
