# server_arkaios.py
from flask import Flask, send_from_directory, jsonify
from pathlib import Path

APP_DIR = Path(__file__).parent
STATIC_DIR = APP_DIR

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

@app.get("/")
def home():
    return send_from_directory(STATIC_DIR, "arkaios.html")

@app.get("/health")
def health():
    return jsonify({"ok": True, "name": "ARKAIOS server", "status": "ready"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)