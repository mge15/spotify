import spotipy
import os
import requests
import json
import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import Flask, request, redirect, g, render_template
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from urllib.parse import quote

# test data

playlist_group_name = "New Playlist"

uris = ["spotify:track:0LtOwyZoSNZKJWHqjzADpW",
        "spotify:track:57RA3JGafJm5zRtKJiKPIm",
        "spotify:track:5RRWirYSE08FPKD6Mx4v0V",
        "spotify:track:4djIFfof5TpbSGRZUpsTXq"]


load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID", default="abc123")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", default="abc456")

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = f"{SPOTIFY_API_BASE_URL}/{API_VERSION}"

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "http://127.0.0.1:8080/callback/q"
SCOPE = "user-follow-read"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}


@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val))
                         for key, val in auth_query_parameters.items()])
    auth_url = f'{SPOTIFY_AUTH_URL}/?{url_args}'
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = f"{SPOTIFY_API_URL}/me"
    profile_response = requests.get(
        user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # get followed users
    friends = ["stellapug1127", "justlivwithit", "sfrost5772"]
    count = len(friends)

    user_followers = f"{SPOTIFY_API_URL}/me/following/contains?type=user&ids="

    for x in friends:
        if friends.index(x) == count - 1:
            user_followers = user_followers + x
        else:
            user_followers = user_followers + f"{x}%2C"

    follower_response = requests.get(user_followers, headers=authorization_header)
    user_data = json.loads(follower_response.text)
    return str(user_data)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
