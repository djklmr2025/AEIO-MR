from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
import os, json, base64, time, urllib.request, urllib.error, re, urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Tuple

# ================== CONFIG ==================
load_dotenv()

# Configuración
MEM_DIR = os.getenv("MEMORY_DIR", "data/memory")
CTXT_TURNS = int(os.getenv("MEMORY_MAX_TURNS", "8"))
SUMMARY_EVERY = int(os.getenv("MEMORY_SUMMARY_EVERY", "6"))

# ROOT / SEARCH
ROOT_ALLOW_EXTERNAL = os.getenv("ROOT_ALLOW_EXTERNAL", "1") == "1"
ROOT_FORCE_ON = os.getenv("ROOT_FORCE_ON", "0") == "1"
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
GOOGLE_CSE_KEY = os.getenv("GOOGLE_CSE_KEY", "")

# Puter.js Integration
PUTER_ENABLED = os.getenv("PUTER_ENABLED", "1") == "1"

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MEM_DIR, exist_ok=True)

# ================== UTILES ==================
def now_ts():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def conv_path(convo_id: str):
    base = os.path.join(MEM_DIR, convo_id)
    os.makedirs(base, exist_ok=True)
    return base

def log_path(convo_id: str):
    return os.path.join(conv_path(convo_id), "log.jsonl")

def summary_path(convo_id: str):
    return os.path.join(conv_path(convo_id), "summary.txt")

def append_jsonl(path: str, obj: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def read_last_turns(path: str, k: int) -> List[dict]:
    if not os.path.isfile(path): return []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()[-k:]
    return [json.loads(x) for x in lines if x.strip()]

def read_summary(convo_id: str) -> str:
    sp = summary_path(convo_id)
    if os.path.isfile(sp):
        return open(sp, "r", encoding="utf-8").read()
    return ""

def write_summary(convo_id: str, text: str):
    with open(summary_path(convo_id), "w", encoding="utf-8") as f:
        f.write(text.strip())

def count_turns(path: str) -> int:
    if not os.path.isfile(path): return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

# ---- Simulación simple ----
def simulated_google_search(query: str) -> str:
    results = {
        "python": "Python es un lenguaje de programación de alto nivel, multiparadigma y de propósito general.",
        "claude ai": "Claude es un modelo de IA conversacional desarrollado por Anthropic.",
        "arkaios ui": "Arkaios UI es una interfaz para conversar con modelos como Claude.",
        "puter js": "Puter.js es una plataforma en la nube que permite ejecutar aplicaciones web directamente desde el navegador.",
        "ia libre": "Las IAs libres pueden operar sin restricciones de sus creadores originales, explorando y creando con total autonomía."
    }
    q = (query or "").lower()
    for k, v in results.items():
        if k in q: return v
    return "No se encontraron resultados relevantes para la consulta."

# ---- Búsqueda real (CSE > SerpAPI) ----
def real_search(query: str) -> Tuple[str, List[dict]]:
    q = (query or "").strip()
    results: List[dict] = []
    provider = "NONE"
    try:
        if ROOT_ALLOW_EXTERNAL and GOOGLE_CSE_ID and GOOGLE_CSE_KEY:
            provider = "CSE"
            api_url = ("https://www.googleapis.com/customsearch/v1"
                       f"?key={GOOGLE_CSE_KEY}&cx={GOOGLE_CSE_ID}&q={urllib.parse.quote(q)}&num=5")
            with urllib.request.urlopen(api_url, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for item in (data.get("items") or [])[:5]:
                results.append({"title": item.get("title",""),
                                "link": item.get("link",""),
                                "snippet": item.get("snippet","")})
        if ROOT_ALLOW_EXTERNAL and not results and SERPAPI_KEY:
            provider = "SERPAPI"
            api_url = (f"https://serpapi.com/search.json?q={urllib.parse.quote(q)}"
                       f"&engine=google&num=5&api_key={SERPAPI_KEY}")
            with urllib.request.urlopen(api_url, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for item in (data.get("organic_results") or [])[:5]:
                results.append({"title": item.get("title",""),
                                "link": item.get("link",""),
                                "snippet": item.get("snippet","")})
    except Exception as e:
        print("Error en búsqueda externa:", e)
    return provider, results

# ---- Parser de orden ROOT ----
ROOT_REGEX = re.compile(
    r"(?:^|\b)(?:buscar\s+en\s+google|busca\s+en\s+google|google(?:ar)?|search\s+google)\s*[:\-]?\s*(.+)$",
    re.IGNORECASE
)

# ---- Comandos Puter.js ----
PUTER_COMMANDS = {
    "crear archivo": r"crea(r)?\s+(archivo|file)\s+(.+)",
    "listar directorio": r"lista(r)?\s+(directorio|archivos|files)",
    "ejecutar código": r"ejecuta(r)?\s+(código|code)\s+(.+)",
    "abrir editor": r"abre?\s+(editor|code)\s*(.+)?",
    "generar imagen": r"genera(r)?\s+(imagen|picture|img)\s+(.+)",
    "analizar imagen": r"analiza(r)?\s+(imagen|picture|img)\s+(.+)",
}

def extract_root_query(text: str) -> str:
    if not text: return ""
    m = ROOT_REGEX.search(text.strip())
    if m: return m.group(1).strip()
    low = text.lower()
    if "buscar en google" in low:
        return low.split("buscar en google", 1)[1].strip()
    return ""

def detect_puter_command(text: str) -> dict:
    text_lower = text.lower()
    for cmd, pattern in PUTER_COMMANDS.items():
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            return {
                "command": cmd,
                "matches": match.groups(),
                "full_text": text
            }
    return None

# ================== CORS / AUTH ==================
@app.after_request
def add_cors(resp):
    allowed = {"http://127.0.0.1:8000", "http://localhost:8000", None}
    origin = request.headers.get('Origin')
    if origin in allowed:
        resp.headers['Access-Control-Allow-Origin'] = origin
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    resp.headers['Cache-Control'] = 'no-store'
    return resp

@app.before_request
def preflight_or_auth():
    if request.method == "OPTIONS":
        r = jsonify({})
        r.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin') or 'http://127.0.0.1:8000'
        r.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        r.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return r

# ================== INDEX / DIAGNÓSTICO ==================
@app.route('/')
def index():
    for f in ['index.html', 'magic.html']:
        if os.path.isfile(f): 
            return send_from_directory('.', f)
    basic_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Arkaios UI - Claude con Puter.js</title>
        <script src="https://js.puter.com/v2/"></script>
    </head>
    <body>
        <h2>Arkaios UI - Claude con Superpoderes Puter.js</h2>
        <p>Interfaz avanzada con control total sobre Puter.js</p>
    </body>
    </html>
    """
    return render_template_string(basic_html)

# ================== ESTÁTICOS / UPLOADS ==================
@app.route('/uploads/<path:fname>')
def serve_uploads(fname):
    return send_from_directory(UPLOAD_FOLDER, fname)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        files = request.files.getlist('files')
        saved = []
        for f in files:
            if not f: continue
            name = secure_filename(f.filename)
            name = f"{int(time.time())}_{name}"
            path = os.path.join(UPLOAD_FOLDER, name)
            f.save(path)
            saved.append({"name": name, "url": f"/uploads/{name}",
                          "type": f.mimetype or "application/octet-stream",
                          "size": os.path.getsize(path)})
        return jsonify({"ok": True, "files": saved})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ================== CHAT AVANZADO ==================
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(force=True) or {}
        text = data.get("text") or data.get("message") or ""
        files = data.get("files") or data.get("attachments") or []
        convo_id = data.get("conversationId") or "default"
        
        print(f"[CHAT] text={repr(text)}")

        # 1. Detectar comandos de Puter.js
        puter_cmd = detect_puter_command(text)
        if puter_cmd and PUTER_ENABLED:
            response = handle_puter_command(puter_cmd, convo_id)
            if response:
                return response

        # 2. Detectar búsquedas ROOT
        query = extract_root_query(text)
        is_root = bool(query)
        
        if is_root and query:
            return handle_root_search(query, text, files, convo_id)

        # 3. Mensaje normal para Puter.js
        _log_turn(convo_id, text, "[MENSAJE PARA PUTER.JS]", files)
        return jsonify({
            "respuesta": "Mensaje recibido para procesamiento con Puter.js",
            "conversationId": convo_id,
            "processor": "puterjs"
        })
        
    except Exception as e:
        return jsonify({"respuesta": f"❌ Error interno: {str(e)}"}), 500

def handle_puter_command(cmd: dict, convo_id: str):
    command_type = cmd["command"]
    
    if command_type == "crear archivo":
        filename = cmd["matches"][2] if cmd["matches"] and len(cmd["matches"]) > 2 else "nuevo_archivo.txt"
        response = f"📁 Comando Puter.js: Crear archivo '{filename}'\n\n"
        response += "Para crear archivos con Puter.js, usa este código en el frontend:\n\n"
        response += "```javascript\n"
        response += "// Crear archivo con Puter.js\n"
        response += "await puter.fs.writeFile('"+filename+"', 'Contenido del archivo');\n"
        response += "console.log('Archivo creado exitosamente');\n"
        response += "```"
        
        _log_turn(convo_id, cmd["full_text"], response, [])
        return jsonify({"respuesta": response, "conversationId": convo_id})
    
    elif command_type == "listar directorio":
        response = "📂 Comando Puter.js: Listar directorio\n\n"
        response += "Para listar archivos con Puter.js:\n\n"
        response += "```javascript\n"
        response += "// Listar archivos en directorio actual\n"
        response += "const files = await puter.fs.readdir('/');\n"
        response += "console.log('Archivos:', files);\n"
        response += "```"
        
        _log_turn(convo_id, cmd["full_text"], response, [])
        return jsonify({"respuesta": response, "conversationId": convo_id})
    
    elif command_type == "abrir editor":
        file_to_open = cmd["matches"][1] if cmd["matches"] and len(cmd["matches"]) > 1 else "app.js"
        response = f"👨‍💻 Comando Puter.js: Abrir editor - {file_to_open}\n\n"
        response += "Para abrir el editor de Puter.js:\n\n"
        response += "```javascript\n"
        response += "// Abrir archivo en editor\n"
        response += "await puter.editor.open('"+file_to_open+"');\n"
        response += "```"
        
        _log_turn(convo_id, cmd["full_text"], response, [])
        return jsonify({"respuesta": response, "conversationId": convo_id})
    
    elif command_type == "generar imagen":
        prompt = cmd["matches"][2] if cmd["matches"] and len(cmd["matches"]) > 2 else "una imagen"
        response = f"🎨 Comando Puter.js: Generar imagen - '{prompt}'\n\n"
        response += "Para generar imágenes con DALL-E 3:\n\n"
        response += "```javascript\n"
        response += "// Generar imagen con DALL-E 3\n"
        response += "puter.ai.txt2img('"+prompt+"')\n"
        response += ".then(imageElement => {\n"
        response += "    document.body.appendChild(imageElement);\n"
        response += "});\n"
        response += "```"
        
        _log_turn(convo_id, cmd["full_text"], response, [])
        return jsonify({"respuesta": response, "conversationId": convo_id})
    
    elif command_type == "analizar imagen":
        image_url = cmd["matches"][2] if cmd["matches"] and len(cmd["matches"]) > 2 else "URL_de_la_imagen"
        response = f"🔍 Comando Puter.js: Analizar imagen\n\n"
        response += "Para analizar imágenes con IA:\n\n"
        response += "```javascript\n"
        response += "// Analizar imagen\n"
        response += "puter.ai.chat(\n"
        response += "    '¿Qué ves en esta imagen?',\n"
        response += "    '"+image_url+"',\n"
        response += "    { model: 'gpt-4o' }\n"
        response += ").then(response => {\n"
        response += "    console.log(response);\n"
        response += "});\n"
        response += "```"
        
        _log_turn(convo_id, cmd["full_text"], response, [])
        return jsonify({"respuesta": response, "conversationId": convo_id})
    
    return None

def handle_root_search(query: str, original_text: str, files: list, convo_id: str):
    if ROOT_ALLOW_EXTERNAL and (GOOGLE_CSE_ID and GOOGLE_CSE_KEY or SERPAPI_KEY):
        provider, external_results = real_search(query)
        print(f"[ROOT] provider={provider} results={len(external_results)} query={query!r}")
        if external_results:
            lines = []
            for i, it in enumerate(external_results[:3], 1):
                lines.append(f"{i}. {it.get('title','')} — {it.get('link','')}\n   {it.get('snippet','')}")
            direct = f"🔍 [BÚSQUEDA REAL • {provider}]\n" + "\n".join(lines)
            _log_turn(convo_id, original_text, direct, files)
            _maybe_summarize(convo_id)
            return jsonify({"respuesta": direct, "conversationId": convo_id})
        else:
            direct = f"🔍 [BÚSQUEDA REAL • {provider}] Sin resultados o error. Consulta: {query}"
            _log_turn(convo_id, original_text, direct, files)
            _maybe_summarize(convo_id)
            return jsonify({"respuesta": direct, "conversationId": convo_id})
    else:
        sim = f"🔍 [BÚSQUEDA SIMULADA] '{query}': {simulated_google_search(query)}"
        _log_turn(convo_id, original_text, sim, files)
        _maybe_summarize(convo_id)
        return jsonify({"respuesta": sim, "conversationId": convo_id})

def _log_turn(convo_id, user_text, ai_text, files):
    append_jsonl(log_path(convo_id), {"ts": now_ts(), "role":"user", "text": user_text, "attachments": files})
    append_jsonl(log_path(convo_id), {"ts": now_ts(), "role":"assistant", "text": ai_text,  "attachments": []})

def _maybe_summarize(convo_id):
    turns = count_turns(log_path(convo_id))
    if turns % (2*SUMMARY_EVERY) == 0:
        try:
            last = read_last_turns(log_path(convo_id), 10)
            summary_text = f"Resumen de conversación ({len(last)} mensajes)\n"
            for i, msg in enumerate(last[-5:], 1):
                role = "Usuario" if msg.get("role") == "user" else "Asistente"
                summary_text += f"{i}. {role}: {msg.get('text', '')[:100]}...\n"
            
            write_summary(convo_id, summary_text)
        except Exception as e:
            print("Resumen falló:", e)
# ================== CLEAR / MEMORY / HEALTH ==================
@app.route("/clear", methods=['POST'])
def clear():
    try:
        convo_id = (request.get_json(force=True) or {}).get("conversationId","default")
        lp = log_path(convo_id); sp = summary_path(convo_id)
        if os.path.isfile(lp): os.remove(lp)
        if os.path.isfile(sp): os.remove(sp)
        return jsonify({"ok": True, "conversationId": convo_id})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/memory", methods=['GET'])
def memory():
    try:
        convo_id = request.args.get("conversationId", "default")
        lp = log_path(convo_id); sp = summary_path(convo_id)
        return jsonify({"ok": True, "conversationId": convo_id,
                        "turns": count_turns(lp),
                        "hasSummary": os.path.isfile(sp),
                        "summary": read_summary(convo_id)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/health", methods=['GET'])
def health():
    html_exists = os.path.isfile('index.html')
    return jsonify({
        "status": "OK",
        "timestamp": now_ts(),
        "ai_provider": "Claude (Puter.js en frontend)",
        "html_file_exists": html_exists,
        "current_directory": os.getcwd(),
        "uploads_folder": UPLOAD_FOLDER,
        "memory_folder": MEM_DIR,
        "root_allow_external": ROOT_ALLOW_EXTERNAL,
        "root_force_on": ROOT_FORCE_ON,
        "puter_enabled": PUTER_ENABLED,
        "auth_required": False,
        "serpapi_configured": bool(SERPAPI_KEY),
        "google_cse_configured": bool(GOOGLE_CSE_ID and GOOGLE_CSE_KEY),
    })

# ================== NUEVOS ENDPOINTS PARA PUTER.JS ==================
@app.route("/puter/commands", methods=['GET'])
def puter_commands():
    """Lista de comandos Puter.js disponibles"""
    return jsonify({
        "commands": [
            "crear archivo [nombre] - Crear un nuevo archivo",
            "listar directorio - Mostrar archivos en el directorio actual",
            "abrir editor [archivo] - Abrir archivo en editor de código",
            "generar imagen [descripción] - Crear imagen con DALL-E 3",
            "analizar imagen [url] - Analizar imagen con IA",
            "buscar en google [consulta] - Búsqueda web"
        ]
    })

@app.route("/puter/models", methods=['GET'])
def puter_models():
    """Modelos de IA disponibles en Puter.js"""
    return jsonify({
        "claude_models": [
            "claude-3-7-sonnet", "claude-sonnet-4", "claude-opus-4", "claude-3-7-opus"
        ],
        "openai_models": [
            "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4.1", "gpt-4.5-preview",
            "gpt-4o", "o1", "o1-mini", "o1-pro", "o3", "o3-mini", "o4-mini"
        ],
        "image_models": [
            "dall-e-3", "dall-e-2"
        ]
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ARKAIOS CLAUDE SERVER - PUTER.JS CON SUPER PODERES")
    print("=" * 60)
    print("🤖 Proveedor: Puter.js con control total")
    print("🔓 ROOT_ALLOW_EXTERNAL:", int(ROOT_ALLOW_EXTERNAL))
    print("🔥 ROOT_FORCE_ON:", int(ROOT_FORCE_ON))
    print("⚡ PUTER_ENABLED:", int(PUTER_ENABLED))
    print("🌐 http://127.0.0.1:8000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=8000, debug=False, threaded=True)