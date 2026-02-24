import streamlit as st
import yt_dlp
import os
import tempfile

st.title("📥 Pluck It Pro: 2026 Force-Bypass")

# Input tokens (Refresh these every few hours if you get a 403)
col1, col2 = st.columns(2)
with col1:
    po_token = st.text_input("PO Token", help="From v1/player payload")
with col2:
    visitor_data = st.text_input("Visitor Data", help="From v1/player payload")

url = st.text_input("YouTube URL:")

if url and st.button("🚀 Pluck Now"):
    # 1. CORE BYPASS OPTIONS
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'source_address': '0.0.0.0', # Critical: Force IPv4
        'nocheckcertificate': True,
        
        # 2. CLIENT SPOOFING (mweb is best for tokens in 2026)
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        
        # 3. MANIFEST BYPASS
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
    }

    # 4. INJECT TOKENS
    if po_token and visitor_data:
        # Prefix varies by client; for mweb it usually needs 'mweb.gvs+'
        p_token = po_token if po_token.startswith("mweb") else f"mweb.gvs+{po_token}"
        ydl_opts['extractor_args']['youtube']['po_token'] = p_token
        ydl_opts['extractor_args']['youtube']['visitor_data'] = visitor_data

    # 5. COOKIE INJECTION
    if "YT_COOKIES" in st.secrets:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            tmp.write(st.secrets["YT_COOKIES"])
            ydl_opts['cookiefile'] = tmp.name
    elif os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            st.success(f"Downloaded: {info.get('title')}")
            # Add download button logic here...
    except Exception as e:
        st.error(f"YouTube security blocked this request: {e}")
