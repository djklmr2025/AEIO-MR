# server_local.py
import os, io, json, time, uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Lectura de PDFs/TXT
from pypdf import PdfReader

# Conector web (opcional)
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

# --------- Config ----------
from dotenv import load_dotenv
load_dotenv()

# Modelo local vía Ollama (http://127.0.0.1:11434)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "llama3.1")   # cambia si quieres otro

BASE_DIR      = Path(__file__).resolve().parent
UPLOAD_ROOT   = BASE_DIR / "uploads"
MEMORY_ROOT   = BASE_DIR / "memory"
ALLOW_DOMAINS = set(d.strip().lower() for d in os.getenv("WEB_ALLOWLIST","").split(",")) if os.getenv("WEB_ALLOWLIST") else set()

UPLOAD_ROOT.mkdir(exist_ok=True)
MEMORY_ROOT.mkdir(exist_ok=True)

MAX_IMAGE_BYTES = 10 * 1024 * 1024
CHUNK_TOKENS = 1800  # no estricto aquí; mantenemos para simetría

# --------- Utilidades ----------
def conv_dir(conversation_id: str) -> Path:
    d = MEMORY_ROOT / secure_filename(conversation_id)
    d.mkdir(exist_ok=True, parents=True)
    (d / "logs").mkdir(exist_ok=True)
    return d

def append_log(conversation_id: str, role: str, content: str, extra: Dict[str,Any]|None=None):
    d = conv_dir(conversation_id)
    row = {
        "ts": datetime.utcnow().isoformat()+"Z",
        "role": role,
        "content": content,
        "extra": extra or {}
    }
    with (d / "history.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False)+"\n")

def load_summary(conversation_id: str) -> str:
    p = conv_dir(conversation_id) / "summary.txt"
    return p.read_text(encoding="utf-8") if p.exists() else ""

def save_summary(conversation_id: str, text: str):
    p = conv_dir(conversation_id) / "summary.txt"
    p.write_text(text, encoding="utf-8")

def list_filesafe(fn: str) -> str:
    return secure_filename(fn).replace("..","_")

def is_allowed_url(url: str) -> bool:
    if not ALLOW_DOMAINS:  # sin allowlist => permitir todo (bajo tu responsabilidad)
        return True
    try:
        import urllib.parse as up
        host = up.urlparse(url).hostname or ""
        return any(host.endswith(dom) for dom in ALLOW_DOMAINS)
    except Exception:
        return False

def read_text_from_pdf(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        chunks=[]
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                chunks.append(t)
        return "\n\n".join(chunks)
    except Exception as e:
        return f"[PDF ERROR] {e}"

# --------- LLM local (Ollama) ----------
def ollama_generate(prompt: str, system: str|None=None) -> str:
    """
    Llama al endpoint /api/generate de Ollama.
    No envía nada fuera de tu máquina.
    """
    payload = {
        "model": LOCAL_MODEL,
        "prompt": prompt if not system else f"<<SYS>>\n{system}\n<</SYS>>\n\n{prompt}",
        "stream": False,
        # Algunos modelos respetan esto:
        "options": {
            # desactiva funciones de seguridad del modelo si lo permite (responsabilidad tuya);
            # nosotros NO vamos a generar contenido ilegal/peligroso aunque el modelo lo permita.
            "temperature": 0.7
        }
    }
    r = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=300)
    r.raise_for_status()
    data = r.json()
    return (data.get("response") or "").strip()

def summarize_incremental(text: str, running_summary: str) -> str:
    sys = ("Eres un asistente que condensa fragmentos en un resumen acumulado claro, "
           "con bullets y secciones, manteniendo hechos clave, nombres y fechas.")
    prompt = f"Resumen actual:\n{running_summary}\n\nNuevo fragmento:\n{text}\n\nDevuelve solo el resumen actualizado."
    return ollama_generate(prompt, sys)

def call_local_llm(system: str, messages: List[Dict[str,str]]) -> str:
    # Construyo prompt con últimas 10 entradas
    history=[]
    if system:
        history.append(f"<<SYS>>\n{system}\n<</SYS>>")
    for m in messages[-10:]:
        history.append(f"{m['role'].upper()}:\n{m['content']}")
    prompt = "\n\n".join(history)
    return ollama_generate(prompt)

# --------- Flask ----------
app = Flask(__name__, static_folder=None)

@app.get("/")
def home():
    return "Arkaios local backend (Ollama) OK", 200

# Subida de adjuntos
@app.post("/upload")
def upload():
    files = request.files.getlist("files")
    saved=[]
    for f in files:
        name = list_filesafe(f.filename or f"file_{uuid.uuid4().hex}")
        dest = UPLOAD_ROOT / name
        f.save(dest)
        saved.append({
            "name": name,
            "url": f"/uploads/{name}",
            "type": f.mimetype,
            "size": dest.stat().st_size
        })
    return jsonify({"files": saved})

@app.get("/uploads/<path:fname>")
def dl(fname):
    return send_from_directory(UPLOAD_ROOT, fname, as_attachment=False)

# Limpiar memoria por conversación
@app.post("/clear")
def clear():
    data = request.get_json(force=True, silent=True) or {}
    cid  = data.get("conversationId") or "default"
    d = conv_dir(cid)
    for p in [d/"summary.txt", d/"history.jsonl"]:
        if p.exists():
            p.unlink()
    for p in (d/"logs").glob("*.log"):
        p.unlink()
    return jsonify({"ok": True})

# Conector Web
@app.post("/web")
def web_search():
    data = request.get_json(force=True) or {}
    query = (data.get("query") or "").strip()
    urls  = data.get("urls") or []
    max_results = int(data.get("max", 5))
    use_fetch = bool(data.get("fetch"))
    results, fetched = [], []

    if query:
        with DDGS() as ddg:
            for r in ddg.text(query, max_results=max_results, safesearch="moderate"):
                results.append({"title": r.get("title"), "url": r.get("href"), "snippet": r.get("body")})

    if use_fetch and urls:
        for u in urls[:max_results]:
            if not is_allowed_url(u):
                fetched.append({"url": u, "error":"blocked_by_allowlist"})
                continue
            try:
                html = requests.get(u, timeout=12).text
                soup = BeautifulSoup(html, "html.parser")
                text = " ".join((soup.get_text(" ", strip=True) or "").split())
                fetched.append({"url": u, "text": text[:12000]})
            except Exception as e:
                fetched.append({"url": u, "error": str(e)})

    return jsonify({"results": results, "fetched": fetched})

# Chat principal
@app.post("/chat")
def chat():
    data = request.get_json(force=True) or {}
    text = (data.get("message") or "").strip()
    attachments = data.get("attachments") or []
    root = bool(data.get("root"))
    cid  = data.get("conversationId") or "default"
    use_web = bool(data.get("use_web"))

    summary = load_summary(cid)
    context_system = f"""
Eres Arkaios (proveedor LOCAL). Usa el 'summary' como memoria de largo plazo de esta conversación.
- Si hay adjuntos, se han subido a /uploads; cuando el user te pida usarlos, coméntalo explícitamente.
- Si 'modo ROOT' está activo: el usuario permite acciones administrativas (CONFIRMA antes de borrar/editar).
Resumen previo:
{summary or '(vacío)'}
"""

    # Extractos mínimos de adjuntos
    attachment_texts=[]
    for a in attachments:
        try:
            url = a.get("url","")
            fpath = (BASE_DIR / url.lstrip("/")).resolve()
            if url.endswith(".pdf") and fpath.exists():
                attachment_texts.append(f"[{a.get('name')}] Extracto:\n"+read_text_from_pdf(fpath)[:4000])
            elif any(url.lower().endswith(ext) for ext in [".txt",".md",".log",".csv"]):
                attachment_texts.append(f"[{a.get('name')}] Extracto:\n"+fpath.read_text(encoding="utf-8", errors="ignore")[:4000])
        except Exception:
            pass

    web_context = ""
    if use_web and text:
        blocks=[]
        try:
            with DDGS() as ddg:
                for r in ddg.text(text, max_results=5, safesearch="moderate"):
                    title=r.get("title") or ""
                    url=r.get("href") or ""
                    body=r.get("body") or ""
                    blocks.append(f"- {title}\n{body}\n{url}")
        except Exception:
            pass
        if blocks:
            web_context = "FUENTES WEB (recientes):\n" + "\n\n".join(blocks)

    prompt = ""
    if attachment_texts:
        prompt += "Adjuntos (extractos):\n" + "\n\n".join(attachment_texts) + "\n\n"
    if web_context:
        prompt += web_context + "\n\n"
    prompt += f"Usuario dice: {text}"

    append_log(cid, "user", text, {"attachments": attachments, "root": root, "use_web": use_web})

    out = call_local_llm(context_system, [{"role":"user","content":prompt}])

    append_log(cid, "assistant", out)
    return jsonify({"respuesta": out})

# Import de carpeta (PDF/TXT => summary.txt)
@app.post("/import_folder")
def import_folder():
    data = request.get_json(force=True) or {}
    cid   = data.get("conversationId") or "default"
    folder= data.get("folder") or ""
    recursive = bool(data.get("recursive"))
    patterns  = data.get("patterns") or ["*.pdf","*.txt","*.md"]

    if not folder:
        return jsonify({"ok":False,"error":"missing folder"}), 400

    root = Path(folder).expanduser()
    if not root.exists():
        return jsonify({"ok":False,"error":"folder_not_found"}), 404

    existing = load_summary(cid)
    updated = existing

    def walk(globp):
        return root.rglob(globp) if recursive else root.glob(globp)

    files = []
    for pat in patterns:
        for p in walk(pat):
            if p.is_file():
                files.append(p)
    files = sorted(files)
    imported = []

    for p in files:
        try:
            if p.suffix.lower()==".pdf":
                text = read_text_from_pdf(p)
            else:
                text = p.read_text(encoding="utf-8", errors="ignore")
            # “resumen incremental”: enviamos chunks al LLM local
            for i in range(0, len(text), 8000):
                chunk = text[i:i+8000]
                updated = summarize_incremental(chunk, updated)
            imported.append(str(p))
        except Exception as e:
            imported.append(f"{p} [ERROR {e}]")

    save_summary(cid, updated)
    append_log(cid, "system", f"import_folder({folder})", {"files": imported})
    return jsonify({"ok":True, "imported": imported, "summary_len": len(updated)})

if __name__ == "__main__":
    # Dev
    app.run(host="127.0.0.1", port=8000, debug=True)
    # Producción Windows (sin ventana consola):
    # from waitress import serve
    # serve(app, host="127.0.0.1", port=8000)
