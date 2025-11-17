from flask import Flask, request, render_template, redirect, url_for, jsonify
import tweet_extractor as twitter
import pipeline as agent
#import Agentic.pipeline as agent
import re
import json
import time
import os
import dotenv
dotenv.load_dotenv()

app = Flask(__name__)

# -------------------------
# USER & TOKEN CONFIG
# -------------------------
USERS = {
    "admin": "admin123",
    "prameth": "ai2025",
    "testuser": "pass123",
    "thrishal": "guntur",
    "shyam": "guntur",
}

TOKENS = {
    1: os.environ.get("token1"),
    2: os.environ.get("token2"),
    3: os.environ.get("token3"),
    4: os.environ.get("token4")
}

COOLDOWN_FILE = "token_cooldowns.json"
COOLDOWN_TIME = 15 * 60 * 1000  # 5 minutes in ms


# -------------------------
# HELPER FUNCTIONS
# -------------------------
def load_cooldowns():
    """Load cooldown timestamps from JSON file (ms since epoch)."""
    if not os.path.exists(COOLDOWN_FILE):
        with open(COOLDOWN_FILE, 'w') as f:
            # initialize with zeros (string keys)
            json.dump({str(i): 0 for i in TOKENS.keys()}, f)
    with open(COOLDOWN_FILE, 'r') as f:
        return json.load(f)


def save_cooldowns(data):
    """Save cooldown timestamps to JSON file."""
    with open(COOLDOWN_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_remaining_ms_for_token(token_str):
    """Return remaining milliseconds of cooldown for a given token string key."""
    cooldowns = load_cooldowns()
    last_used = int(cooldowns.get(token_str, 0))
    now = int(time.time() * 1000)
    remaining = max(0, COOLDOWN_TIME - (now - last_used))
    return remaining


# -------------------------
# LOGIN ROUTES
# -------------------------
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in USERS and USERS[username] == password:
        return redirect(url_for('landing', user=username))
    else:
        return render_template("index.html", error="Invalid username or password")


# -------------------------
# LANDING PAGE
# -------------------------
@app.route('/landing')
def landing():
    user = request.args.get('user', 'Guest')
    return render_template("landing.html", user=user)


# -------------------------
# CHECK TOKEN (AJAX) - returns remaining cooldown seconds
# -------------------------
@app.route('/check_token', methods=['GET'])
def check_token():
    token = request.args.get('token')
    if not token or token not in [str(k) for k in TOKENS.keys()]:
        return jsonify({"error": "Invalid token"}), 400

    remaining_ms = get_remaining_ms_for_token(token)
    return jsonify({
        "token": token,
        "remaining_ms": remaining_ms,
        "remaining_seconds": int(remaining_ms // 1000)
    })


# -------------------------
# UPDATE TOKEN COOLDOWN (AJAX) - server-side write; optional if using /extract update
# -------------------------
@app.route('/update_cooldown', methods=['POST'])
def update_cooldown():
    data = request.get_json()
    token = str(data.get('token'))
    if token not in [str(k) for k in TOKENS.keys()]:
        return jsonify({"error": "Invalid token"}), 400

    cooldowns = load_cooldowns()
    cooldowns[token] = int(time.time() * 1000)
    save_cooldowns(cooldowns)
    return jsonify({"message": f"Token {token} cooldown updated successfully"})


# -------------------------
# TWEET EXTRACTION + VERDICT
# (Only update token cooldown AFTER a successful extraction & verdict)
# -------------------------
@app.route('/extract', methods=['POST'])
async def extract():
    url = request.form.get('tweet_url')
    selected_token = request.form.get('selected_token')

    if not url:
        return "Tweet URL is required.", 400
    if not selected_token:
        return "Please select a token before analyzing.", 400

    # Validate token number
    if selected_token not in [str(k) for k in TOKENS.keys()]:
        return f"Invalid token selected: {selected_token}", 400

    # Check token cooldown BEFORE attempting to use it
    remaining_ms = get_remaining_ms_for_token(selected_token)
    if remaining_ms > 0:
        remaining_seconds = remaining_ms // 1000
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        return (f"⏳ Token {selected_token} is cooling down. "
                f"Try again in {minutes}m {seconds}s."), 429

    # Proceed to extract using the selected token's bearer string
    token_int = int(selected_token)
    bearer = TOKENS.get(token_int)
    if not bearer:
        return f"Bearer token for token id {selected_token} not configured on server.", 500

    # Extract tweet and generate verdict -- wrap in try/except
    try:
        tweet_id = url.rstrip("/").split("/")[-1]
        tweet = twitter.extract_tweet_info(tweet_id, bearer)
        if not tweet:
            # extraction failed (tweet missing, invalid id, or API error)
            return "Failed to extract tweet. Check the URL or token privileges.", 502

        # If you want more robust checks, verify required fields:
        if 'text' not in tweet or 'username' not in tweet:
            return "Tweet data incomplete; extraction likely failed.", 502

        # SUCCESS -> update cooldown timestamp for this token
        cooldowns = load_cooldowns()
        cooldowns[str(selected_token)] = int(time.time() * 1000)
        save_cooldowns(cooldowns)

        # Run your pipeline (this may raise — you can catch and return)
        verdict = agent.run_pipeline(tweet_text=tweet['text'], username=tweet['username'])
    except Exception as e:
        # Do NOT update cooldown if extraction or verdict fails
        return f"Error during processing: {str(e)}", 500
    
    # Render details page
    return render_template("details.html", tweet=tweet, verdict=verdict)


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8000)
