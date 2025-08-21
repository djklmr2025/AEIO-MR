from flask import Flask, request, jsonify, make_response
import json, urllib.request

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3"

app = Flask(__name__)

# ---- CORS básico
@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return resp

@app.route("/chat", methods=["OPTIONS"])
def preflight():
    return make_response(("", 204))

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or data.get("mensaje") or "").strip()
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Eres Arkaios, un asistente útil y directo."},
            {"role": "user", "content": user_message}
        ],
        "stream": False
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type":"application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return jsonify({"reply": data["message"]["content"]})
    except Exception as e:
        return jsonify({"error": f"Ollama no respondió: {e}"}), 502

@app.route("/")
def root():
    return jsonify({"ok": True, "msg":"Arkaios (Ollama) está vivo"})

# Evita 404 amarillo por el favicon
@app.route("/favicon.ico")
def favicon():
    return ("", 204)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
