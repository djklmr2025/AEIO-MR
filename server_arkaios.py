# server_arkaios.py — ARKAIOS server (logging persistente + tareas + daemon)
from flask import Flask, send_from_directory, jsonify, request
from pathlib import Path
from threading import Thread, Event
from datetime import datetime
import time, os, json

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

APP_DIR = Path(__file__).parent.resolve()
STATIC_DIR = APP_DIR
MEM_DIR = Path(os.getenv("MEMORY_DIR", "data/memory")).resolve()
MEM_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = MEM_DIR / "arkaios_log.jsonl"
SESSION_PATH = MEM_DIR / "arkaios_session_last.json"
TASKS_PATH = MEM_DIR / "tasks.json"
DOCS_PATH = MEM_DIR / "docs.html"  # opcional: carta de habilidades embebida

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

@app.get("/")
def home():
    return send_from_directory(STATIC_DIR, "arkaios.html")

@app.get("/health")
def health():
    return jsonify({"ok": True, "name": "ARKAIOS server", "status": "ready", "mem_dir": str(MEM_DIR)})

# --- Persistence APIs ---
@app.post("/api/log")
def api_log():
    try:
        payload = request.get_json(force=True) or {}
        rows = payload.get("rows", [])
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            for r in rows:
                r.setdefault("ts", int(time.time()*1000))
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        return jsonify({"ok": True, "written": len(rows)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.post("/api/session")
def api_session():
    try:
        snap = request.get_json(force=True) or {}
        SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        SESSION_PATH.write_text(json.dumps({"ts": int(time.time()*1000), "snapshot": snap}, ensure_ascii=False, indent=2), encoding="utf-8")
        return jsonify({"ok": True, "path": str(SESSION_PATH)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.get("/api/log")
def api_log_read():
    try:
        if not LOG_PATH.exists():
            return jsonify({"ok": True, "lines": []})
        lines = LOG_PATH.read_text(encoding="utf-8").strip().splitlines()[-200:]
        return jsonify({"ok": True, "lines": lines})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Tasks (simple daemon) ---
@app.get("/api/tasks")
def get_tasks():
    try:
        if TASKS_PATH.exists():
            data = json.loads(TASKS_PATH.read_text(encoding="utf-8") or '{"tasks":[]}')
        else:
            data = {"tasks": [{"id":"demo-hello","title":"Tarea demo","seen":False,"created_at":datetime.utcnow().isoformat()+"Z"}]}
            TASKS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return jsonify({"ok": True, **data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.post("/api/tasks")
def post_tasks():
    try:
        data = request.get_json(force=True) or {"tasks": []}
        TASKS_PATH.parent.mkdir(parents=True, exist_ok=True)
        TASKS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return jsonify({"ok": True, "path": str(TASKS_PATH)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Docs embebida (opcional) ---
@app.get("/docs")
def docs():
    try:
        if DOCS_PATH.exists():
            return DOCS_PATH.read_text(encoding="utf-8")
        html = """<!doctype html><meta charset="utf-8"><title>ARKAIOS Docs</title>
        <style>body{font-family:system-ui;max-width:900px;margin:2rem auto;padding:0 1rem;color:#0f172a}
        code{background:#f1f5f9;padding:.1rem .3rem;border-radius:6px}</style>
        <h1>ARKAIOS — Carta de habilidades</h1>
        <ul>
          <li><b>img: &lt;prompt&gt;</b> → texto-a-imagen si hay puente; guarda en <code>/home</code>.</li>
          <li><b>analizar imagen &lt;n|url&gt;</b> → si hay visión, la usa; si no, conserva adjuntos.</li>
          <li><b>listar &lt;ruta&gt;</b> (por defecto <code>/home</code>)</li>
          <li><b>descomprimir &lt;archivo.zip&gt;</b> → extrae a <code>/home</code>.</li>
          <li><b>crear archivo &lt;ruta&gt;: &lt;contenido&gt;</b> / <b>leer archivo &lt;ruta&gt;</b></li>
        </ul>"""
        DOCS_PATH.write_text(html, encoding="utf-8")
        return html
    except Exception as e:
        return f"Error generando docs: {e}", 500

# --- Daemon de latido ---
stop_event = Event()
def daemon_loop():
    hb_file = MEM_DIR / "daemon_heartbeat.txt"
    while not stop_event.is_set():
        try:
            hb_file.write_text(datetime.utcnow().isoformat()+"Z", encoding="utf-8")
            # marcar tareas nuevas como 'seen' la primera vez que el daemon las toca
            if TASKS_PATH.exists():
                obj = json.loads(TASKS_PATH.read_text(encoding="utf-8") or "{}")
                changed = False
                for t in obj.get("tasks", []):
                    if not t.get("seen"):
                        t["seen"] = True
                        t["seen_at"] = datetime.utcnow().isoformat()+"Z"
                        changed = True
                if changed:
                    TASKS_PATH.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
        time.sleep(3)

daemon_thr = Thread(target=daemon_loop, daemon=True)
daemon_thr.start()

if __name__ == "__main__":
    print("🚀 Servidor ARKAIOS iniciando…")
    print("🧠 Memory dir:", MEM_DIR)
    print("🌐 http://127.0.0.1:5000/")
    try:
        app.run(host="127.0.0.1", port=5000, debug=True)
    finally:
        stop_event.set(); daemon_thr.join(timeout=2)
