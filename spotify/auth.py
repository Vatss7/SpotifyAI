import uuid
import os 
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI


def show_login_button():
    if 'sp_oauth' not in st.session_state:
        st.error("OAuth client not initialized")
        return

    auth_url = st.session_state.sp_oauth.get_authorize_url()

    st.markdown(f"""
        <style>
            html, body, .main {{
                height: 100%;
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #121212, #1DB954 20%, #191414 60%);
                color: #f5f5f5;
            }}

            .content-wrapper {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                min-height: 100vh;
                padding-top: 80px;
                text-align: center;
            }}

            .spotify-logo {{
                width: 110px;
                height: 110px;
                margin-bottom: 25px;
            }}

            .login-button {{
                background-color: #1DB954;
                color: white !important;
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 40px;
                padding: 12px 30px;
                text-decoration: none !important;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
                cursor: pointer;
                transition: 
                    background-color 0.3s ease,
                    transform 0.3s ease,
                    box-shadow 0.3s ease,
                    border-radius 0.3s ease;
                margin-bottom: 20px;
            }}

            .login-button:hover {{
                background-color: #1ed760;
                transform: translateY(-3px);
                box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.3);
                border-radius: 50px;
            }}

            .welcome-text {{
                font-size: 18px;
                color: #e0e0e0;
                max-width: 600px;
                margin: 0 auto;
                line-height: 1.6;
            }}

            .footer {{
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background-color: #121212;
                color: #bbb;
                text-align: center;
                padding: 12px 0;
                font-size: 13px;
                border-top: 1px solid #333;
            }}
        </style>

        <div class="content-wrapper">
            <img class="spotify-logo" src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" alt="Spotify Logo" />
            <a href="{auth_url}" class="login-button">Login to Spotify</a>
            <div class="welcome-text">
                Welcome to <strong>SpotifyAI</strong> — where your next favorite track finds you.
            </div>
        </div>

        <div class="footer">
            <strong>SpotifyAI</strong> &copy; 2025 Registered Trademark. All rights reserved.
        </div>
    """, unsafe_allow_html=True)




def spotify_authenticate():
    scope = "playlist-modify-private playlist-modify-public user-read-private user-read-email"
    
    # Ensure the .spotifycache directory exists
    cache_dir = os.path.join(os.getcwd(), ".spotifycache")
    os.makedirs(cache_dir, exist_ok=True)

    if 'spotify_cache_path' not in st.session_state:
        # Store cache files in the .spotifycache directory
        st.session_state.spotify_cache_path = os.path.join(cache_dir, f".spotifycache-{uuid.uuid4()}")

    if 'sp_oauth' not in st.session_state:
        st.session_state.sp_oauth = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope,
            cache_path=st.session_state.spotify_cache_path,
            show_dialog=True
        )

    # Token validation check
    if 'token_info' in st.session_state:
        try:
            sp = spotipy.Spotify(auth=st.session_state.token_info['access_token'])
            sp.current_user()  # Test authentication
        except Exception:
            st.session_state.pop('token_info', None)
            st.rerun()

    query_params = st.query_params
    code = query_params.get("code")

    if code and "code_processed" not in st.session_state:
        try:
            token_info = st.session_state.sp_oauth.get_access_token(code)
            st.session_state.token_info = token_info
            st.session_state.code_processed = True
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")
            st.session_state.pop("token_info", None)
            return None

    token_info = st.session_state.get("token_info")

    if not token_info:
        show_login_button()
        return None

    if st.session_state.sp_oauth.is_token_expired(token_info):
        try:
            token_info = st.session_state.sp_oauth.refresh_access_token(
                token_info['refresh_token']
            )
            st.session_state.token_info = token_info
        except Exception as e:
            st.error(f"Token refresh failed: {str(e)}")
            st.session_state.pop("token_info", None)
            show_login_button()
            return None

    return spotipy.Spotify(auth=token_info["access_token"])



