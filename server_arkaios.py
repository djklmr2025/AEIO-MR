# server_arkaios.py — ARKAIOS server (UI split + auth hotfix + endpoints)
import os, json, base64, uuid, time, logging
from datetime import datetime
from pathlib import Path
from threading import Thread, Event

from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS

# --- (Opcional) Google token verification ---
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as grequests
    HAVE_GOOGLE = True
except Exception:
    HAVE_GOOGLE = False

# ========== CONFIG ==========
APP_DIR = Path(__file__).parent.resolve()
STATIC_DIR = APP_DIR               # sirve index.html / arkaios-integrated.html / Puter.js desde aquí
STORAGE = Path(os.getenv("ARK_STORAGE", "data")).resolve()
MEM_DIR = Path(os.getenv("MEMORY_DIR", str(STORAGE / "memory"))).resolve()

LOG_PATH = MEM_DIR / "arkaios_log.jsonl"
SESSION_PATH = MEM_DIR / "arkaios_session_last.json"
TASKS_PATH = MEM_DIR / "tasks.json"
DOCS_PATH = MEM_DIR / "docs.html"

STORAGE.mkdir(parents=True, exist_ok=True)
MEM_DIR.mkdir(parents=True, exist_ok=True)

# Client ID recomendado para validación estricta (opcional)
GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "1077454579238-qlgvl5g039hj2f1hjcpkbp9n0m1k3ql6.apps.googleusercontent.com",
)

# ========== LOGGING ==========
logger = logging.getLogger("arkaios")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
logger.addHandler(ch)

def log_json(event: dict):
    """Añade una línea JSONL al log estructurado."""
    try:
        event.setdefault("ts", int(time.time() * 1000))
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"No se pudo escribir log JSONL: {e}")

# ========== APP ==========
app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
CORS(app, resources={r"/*": {"origins": "*"}})

SESSIONS = {}  # token -> {"email":..., "name":..., "iat":...}

# ===== Util =====
def ok(data=None, **kw):
    obj = {"ok": True}
    if isinstance(data, dict):
        obj.update(data)
    if kw:
        obj.update(kw)
    return jsonify(obj)

def err(msg, code=400, **kw):
    payload = {"ok": False, "error": str(msg)}
    payload.update(kw)
    return jsonify(payload), code

# ====== Front estático ======

# /  -> index.html (login)
@app.get("/")
def home():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return send_from_directory(STATIC_DIR, "index.html")
    return jsonify({"error": "index.html no encontrado"}), 404

# /app -> arkaios-integrated.html (interfaz principal)
@app.get("/app")
def app_page():
    arkaios_path = STATIC_DIR / "arkaios-integrated.html"
    if arkaios_path.exists():
        return send_from_directory(STATIC_DIR, "arkaios-integrated.html")
    return jsonify({"error": "arkaios-integrated.html no encontrado"}), 404

# /claude (opcional) -> Puter.js
@app.get("/claude")
def claude():
    cla = STATIC_DIR / "Puter.js"
    if cla.exists():
        return send_from_directory(STATIC_DIR, "Puter.js")
    return err("Interfaz Claude no encontrada", 404)

# ====== Health ======
@app.get("/health")
def health():
    data = {
        "ok": True,
        "name": "ARKAIOS server",
        "status": "ready",
        "mem_dir": str(MEM_DIR),
        "interfaces": {
            "gpt": (STATIC_DIR / "arkaios-integrated.html").exists(),
            "claude": (STATIC_DIR / "Puter.js").exists(),
        },
    }
    return jsonify(data)

# ====== Auth (Google GIS) con HOTFIX ======
@app.post("/auth/google")
def auth_google():
    body = request.get_json(force=True) or {}
    credential = body.get("credential")
    logger.debug(f"/auth/google recibido. HAVE_GOOGLE={HAVE_GOOGLE}")
    email = "demo@arkaios.local"
    name = "Demo User"

    if credential and HAVE_GOOGLE:
        try:
            info = id_token.verify_oauth2_token(credential, grequests.Request())
            # En producción, valida el aud si quieres forzar tu client id:
            # if info.get("aud") != GOOGLE_CLIENT_ID:
            #     raise ValueError("aud inválido")
            email = info.get("email", email)
            name = info.get("name", name)
            logger.info(f"Google OK para {email}")
        except Exception as e:
            logger.warning(f"Fallo verificación Google, usando modo demo: {e}")
    else:
        logger.warning("Sin credential o sin libs de Google; usando modo demo.")

    tok = uuid.uuid4().hex
    SESSIONS[tok] = {"email": email, "name": name, "iat": int(time.time())}
    log_json({"type": "login", "email": email})
    return ok(token=tok, user={"email": email, "name": name})

# ====== Middleware liviano de sesión ======
def require_auth():
    tok = request.args.get("token") or (request.get_json(silent=True) or {}).get("token")
    return SESSIONS.get(tok)

# ====== Chat (placeholder) ======
@app.post("/chat")
def chat():
    body = request.get_json(force=True) or {}
    user = require_auth()
    who = user["email"] if user else "anon"
    msg = (body.get("message") or "").strip()
    logger.debug(f"/chat {who}: {msg!r}")
    log_json({"type": "chat", "user": who, "message": msg})
    reply = f"[{who}] Recibí: {msg}. (Demo: conecta tu modelo real en /chat)"
    return ok(reply=reply)

# ====== Imagen (demo) ======
@app.post("/image")
def image():
    body = request.get_json(force=True) or {}
    prompt = body.get("prompt") or ""
    logger.debug(f"/image prompt={prompt!r}")
    # Demo: imagen placeholder
    seed = uuid.uuid4().hex[:8]
    url = f"https://picsum.photos/seed/{seed}/768"
    log_json({"type": "image", "prompt": prompt, "url": url})
    return ok(url=url, prompt=prompt)

# ====== Video (demo) ======
@app.post("/video")
def video():
    body = request.get_json(force=True) or {}
    prompt = body.get("prompt") or ""
    logger.debug(f"/video prompt={prompt!r}")
    url = "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"
    log_json({"type": "video", "prompt": prompt, "url": url})
    return ok(url=url, prompt=prompt)

# ====== Archivos ======
@app.get("/files")
def list_files():
    items = []
    for p in STORAGE.glob("**/*"):
        if p.is_file():
            items.append(str(p.relative_to(STORAGE)))
    logger.debug(f"/files -> {len(items)}")
    return ok(files=items)

@app.post("/new")
def new_file():
    body = request.get_json(force=True) or {}
    name = (body.get("name") or "").strip()
    if not name:
        return err("missing name")
    path = STORAGE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    log_json({"type": "file_new", "name": name})
    return ok()

@app.post("/save")
def save_file():
    body = request.get_json(force=True) or {}
    name = (body.get("name") or "").strip()
    content = body.get("content") or ""
    if not name:
        return err("missing name")
    path = STORAGE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(content, str):
        return err("content must be string")
    path.write_text(content, encoding="utf-8")
    log_json({"type": "file_save", "name": name, "size": len(content)})
    return ok()

# ====== Memoria simple ======
MEM_FILE = STORAGE / "mem.json"

def _mem_load():
    if MEM_FILE.exists():
        try:
            return json.loads(MEM_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _mem_save(d):
    MEM_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEM_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

@app.route("/mem", methods=["GET", "POST"])
def mem():
    if request.method == "POST":
        body = request.get_json(force=True) or {}
        key = (body.get("key") or "").strip()
        value = body.get("value")
        if not key:
            return err("missing key")
        d = _mem_load()
        d[key] = value
        _mem_save(d)
        log_json({"type": "mem_set", "key": key})
        return ok()
    else:
        key = (request.args.get("key") or "").strip()
        d = _mem_load()
        val = d.get(key) if key else None
        return ok(value=val)

# ====== Analizar adjuntos ======
@app.post("/analyze")
def analyze():
    body = request.get_json(force=True) or {}
    name = body.get("name") or "upload.bin"
    mime = body.get("mime") or "application/octet-stream"
    b64 = body.get("data") or ""
    try:
        raw = base64.b64decode(b64, validate=True)
    except Exception:
        return err("invalid base64")
    dest = STORAGE / "uploads" / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    preview_url = f"/raw/uploads/{name}" if mime.startswith("image/") else None
    summary = f"Archivo '{name}' ({mime}), {len(raw)} bytes. Guardado en servidor."
    log_json({"type": "analyze", "name": name, "mime": mime, "bytes": len(raw)})
    return ok(summary=summary, preview_url=preview_url)

# Sirve cualquier archivo guardado dentro de STORAGE de forma segura
@app.get("/raw/<path:subpath>")
def raw(subpath):
    base = STORAGE.resolve()
    target = (base / subpath).resolve()
    # Evita path traversal
    if base != target and base not in target.parents:
        return err("Forbidden", 403)
    if target.is_file():
        return send_from_directory(str(target.parent), target.name)
    return err("Not found", 404)

# ====== Utilidades (logs/sesión/tasks/docs/status) ======
@app.post("/api/log")
def api_log():
    payload = request.get_json(force=True) or {}
    rows = payload.get("rows", [])
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        for r in rows:
            r.setdefault("ts", int(time.time() * 1000))
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return ok(written=len(rows))

@app.get("/api/log")
def api_log_read():
    if not LOG_PATH.exists():
        return ok(lines=[])
    lines = LOG_PATH.read_text(encoding="utf-8").strip().splitlines()[-200:]
    return ok(lines=lines)

@app.post("/api/session")
def api_session():
    snap = request.get_json(force=True) or {}
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.write_text(
        json.dumps({"ts": int(time.time() * 1000), "snapshot": snap}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return ok(path=str(SESSION_PATH))

@app.get("/api/tasks")
def get_tasks():
    if TASKS_PATH.exists():
        data = json.loads(TASKS_PATH.read_text(encoding="utf-8") or '{"tasks":[]}')
    else:
        data = {
            "tasks": [{
                "id": "demo-hello",
                "title": "Tarea demo",
                "seen": False,
                "created_at": datetime.utcnow().isoformat() + "Z",
            }]
        }
        TASKS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return ok(**data)

@app.post("/api/tasks")
def post_tasks():
    data = request.get_json(force=True) or {"tasks": []}
    TASKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TASKS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return ok(path=str(TASKS_PATH))

@app.get("/docs")
def docs():
    if DOCS_PATH.exists():
        return DOCS_PATH.read_text(encoding="utf-8")
    html = """<!doctype html>
<meta charset="utf-8">
<title>ARKAIOS Docs</title>
<style>
  body{font-family:system-ui;max-width:900px;margin:2rem auto;padding:0 1rem;color:#0f172a;background:#f8fafc}
  code{background:#f1f5f9;padding:.2rem .4rem;border-radius:6px;border:1px solid #e2e8f0}
  h1{color:#1e293b;border-bottom:2px solid #6366f1;padding-bottom:8px}
  li{margin:6px 0}
</style>
<h1>ARKAIOS — Carta de habilidades</h1>
<ul>
  <li><b>/img &lt;prompt&gt;</b> → texto-a-imagen (demo picsum)</li>
  <li><b>/video &lt;prompt&gt;</b> → placeholder 5s</li>
  <li><b>/files</b>, <b>/new</b>, <b>/save</b></li>
  <li><b>/mem set clave | valor</b> / <b>/mem get clave</b></li>
  <li><b>/analyze</b> adjuntos (preview para imágenes)</li>
</ul>
<h2>Endpoints</h2>
<ul>
  <li><code>POST /auth/google</code>, <code>POST /chat</code>, <code>POST /image</code>, <code>POST /video</code></li>
  <li><code>GET /files</code>, <code>POST /new</code>, <code>POST /save</code></li>
  <li><code>GET/POST /mem</code>, <code>POST /analyze</code>, <code>GET /raw/&lt;path&gt;</code></li>
  <li><code>GET /health</code>, <code>GET /api/status</code></li>
</ul>"""
    DOCS_PATH.write_text(html, encoding="utf-8")
    return html

@app.get("/api/status")
def api_status():
    interfaces = {
        "gpt_interface": (STATIC_DIR / "arkaios-integrated.html").exists(),
        "claude_interface": (STATIC_DIR / "Puter.js").exists(),
    }
    memory_status = {
        "log_exists": LOG_PATH.exists(),
        "session_exists": SESSION_PATH.exists(),
        "tasks_exists": TASKS_PATH.exists(),
    }
    return ok(
        timestamp=datetime.utcnow().isoformat() + "Z",
        interfaces=interfaces,
        memory=memory_status,
        memory_dir=str(MEM_DIR),
    )

# ====== Daemon ======
stop_event = Event()
def daemon_loop():
    hb_file = MEM_DIR / "daemon_heartbeat.txt"
    while not stop_event.is_set():
        try:
            hb_file.write_text(datetime.utcnow().isoformat() + "Z", encoding="utf-8")
            # marcar tareas demo como vistas
            if TASKS_PATH.exists():
                obj = json.loads(TASKS_PATH.read_text(encoding="utf-8") or "{}")
                changed = False
                for t in obj.get("tasks", []):
                    if not t.get("seen"):
                        t["seen"] = True
                        t["seen_at"] = datetime.utcnow().isoformat() + "Z"
                        changed = True
                if changed:
                    TASKS_PATH.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Daemon error: {e}")
        time.sleep(3)

daemon_thr = Thread(target=daemon_loop, daemon=True)
daemon_thr.start()

# ====== Main ======
if __name__ == "__main__":
    logger.info("🚀 Servidor ARKAIOS iniciando…")
    logger.info(f"📂 STORAGE: {STORAGE}")
    logger.info(f"🧠 MEM_DIR: {MEM_DIR}")
    logger.info("🔗 Endpoints clave: /auth/google /chat /image /video /files /new /save /mem /analyze /raw /health")
    logger.info("🌐 UI: http://127.0.0.1:5000/")
    logger.info("📜 Docs: http://127.0.0.1:5000/docs  |  Health: http://127.0.0.1:5000/health")

    try:
        app.run(host="127.0.0.1", port=5000, debug=True)
    finally:
        stop_event.set()
        daemon_thr.join(timeout=2)
