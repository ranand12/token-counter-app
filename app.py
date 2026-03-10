"""Token Counter Web App"""

import json
import os
import urllib.request
import urllib.error
import logging

from flask import Flask, request, jsonify, send_file

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY", "")
API_BASE = "https://generativelanguage.googleapis.com/v1beta"

@app.route("/")
def index():
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    logger.info(f"Serving index from: {index_path}")
    logger.info(f"File exists: {os.path.exists(index_path)}")
    logger.info(f"All files: {os.listdir(os.path.dirname(os.path.abspath(__file__)))}")
    return send_file(index_path)

@app.route("/models.html")
def models_page():
    models_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models.html")
    return send_file(models_path)

@app.route("/count", methods=["POST"])
def count_tokens():
    data = request.get_json()
    text = data.get("text", "")
    model = data.get("model", "gemini-2.0-flash")

    if not text.strip():
        return jsonify({"totalTokens": 0})

    url = f"{API_BASE}/models/{urllib.request.quote(model, safe='')}:countTokens?key={urllib.request.quote(API_KEY, safe='')}"
    payload = json.dumps({"contents": [{"parts": [{"text": text}]}]}).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return jsonify(json.loads(resp.read()))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read()) if e.readable() else {}
        msg = body.get("error", {}).get("message", f"API error ({e.code})")
        return jsonify({"error": msg}), e.code

@app.route("/models", methods=["GET"])
def list_models():
    page_token = request.args.get("pageToken", "")
    url = f"{API_BASE}/models?key={urllib.request.quote(API_KEY, safe='')}&pageSize=1000"
    if page_token:
        url += f"&pageToken={urllib.request.quote(page_token, safe='')}"

    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return jsonify(json.loads(resp.read()))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read()) if e.readable() else {}
        msg = body.get("error", {}).get("message", f"API error ({e.code})")
        return jsonify({"error": msg}), e.code

if __name__ == "__main__":
    if not API_KEY:
        print("WARNING: GOOGLE_API_KEY not set")
    app.run(debug=True, host="0.0.0.0", port=8080)
