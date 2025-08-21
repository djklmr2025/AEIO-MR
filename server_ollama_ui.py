from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os, json, time, urllib.request, urllib.error

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"  # puerto correcto
MODEL = "llama3.1:8b"                            # que exista en "ollama list"

app = Flask(__name__, static_folder=".", static_url_path="")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

conversation_history = []

@app.after_request
def cors(r):
    r.headers["Access-Control-Allow-Origin"]  = "*"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    r.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return r

@app.route("/")
def home():
    return send_from_directory(".", "magic_ollama.html")

@app.route("/favicon.ico")
def fav(): return ("", 204)

@app.route("/clear", methods=["POST"])
def clear():
    conversation_history.clear()
    return jsonify({"status":"Memoria borrada"})

@app.route("/upload", methods=["POST"])
def upload():
    if "files" not in request.files:
        return jsonify({"error": "No se enviaron archivos"}), 400
    files = request.files.getlist("files")
    saved = []
    for file in files:
        fname = secure_filename(file.filename)
        fpath = os.path.join(UPLOAD_FOLDER, fname)
        file.save(fpath)
        saved.append({
            "name": fname,
            "url": f"/uploads/{fname}",
            "type": file.mimetype,
            "size": os.path.getsize(fpath)
        })
    return jsonify({"files": saved})

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/chat", methods=["OPTIONS"])
def preflight(): return ("", 204)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("mensaje") or data.get("message") or "").strip()
    attachments = data.get("attachments", [])

    if attachments:
        files_info = "\n".join([f"Adjunto: {a['name']} ({a['type']}) -> {a['url']}" for a in attachments])
        user_message = f"{user_message}\n\n{files_info}" if user_message else files_info

    if not user_message:
        return jsonify({"respuesta":"No se recibió contenido válido"}), 400

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
            txt = data["message"]["content"]
            conversation_history.append({"role":"user","text":user_message})
            conversation_history.append({"role":"assistant","text":txt})
            return jsonify({"respuesta": txt})
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        return jsonify({"respuesta": f"❌ Ollama HTTP {e.code}: {detail}"}), 502
    except Exception as e:
        return jsonify({"respuesta": f"❌ Ollama no respondió: {e}"}), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
