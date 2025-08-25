from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
import os, json, base64, time, urllib.request, urllib.error, uuid
from datetime import datetime
from dotenv import load_dotenv
from typing import List

# ================== CONFIG ==================
# ================== CONFIG ==================
load_dotenv()

# CORREGIDO: Usar variable de entorno correctamente
API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
# CORREGIDO: URL correcta
BASE    = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# Memoria
MEM_DIR = os.getenv("MEMORY_DIR", "data/memory")             # carpeta raíz de memorias
CTXT_TURNS = int(os.getenv("MEMORY_MAX_TURNS", "8"))         # nº de turnos recientes al contexto
SUMMARY_EVERY = int(os.getenv("MEMORY_SUMMARY_EVERY", "6"))  # cada cuántos turnos actualizar resumen

# Archivos / servidor
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
    # lectura eficiente del final
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

def to_gemini_inline(path, mime):
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("utf-8")
    return {"inlineData": {"data": b64, "mimeType": mime or "application/octet-stream"}}

def http_json(url: str, payload: dict, timeout=60):
    # Añadir API key como parámetro de query
    api_url = f"{url}?key={API_KEY}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        api_url, 
        data=data, 
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        error_detail = e.read().decode("utf-8", "ignore")
        print(f"HTTP Error {e.code}: {error_detail}")
        raise

# ================== CORS BÁSICO ==================
@app.after_request
def add_cors(resp):
    # Permite tu dominio de Vercel/Netlify
    allowed_origins = [
        "http://localhost:3000",
        "https://tu-app.vercel.app",
        "https://tu-app.netlify.app"
    ]
    
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        resp.headers['Access-Control-Allow-Origin'] = origin
    
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    resp.headers['Cache-Control'] = 'no-store'
    return resp

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        resp = jsonify({})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return resp

# ================== ARCHIVOS ESTÁTICOS ==================
@app.route('/')
def index():
    # ← Aquí debe empezar la indentación (4 espacios)
    html_files = ['index.html', 'magic_gemini.html', '']
    
    # Buscar el archivo HTML en el directorio actual
    for html_file in html_files:
        if os.path.isfile(html_file):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content, 200, {'Content-Type': 'text/html; charset=utf-8'}
            except Exception as e:
                print(f"Error leyendo {html_file}: {e}")
                continue
    
    # Si no encontramos ningún archivo HTML, devolver HTML de emergencia
    emergency_html = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Arkaios UI - Error</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }}
            .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
            .error {{ background: #2d1b1b; border: 1px solid #5c2929; border-radius: 8px; padding: 20px; margin: 20px 0; }}
            .success {{ background: #1b2d1b; border: 1px solid #2d5c29; border-radius: 8px; padding: 20px; margin: 20px 0; }}
            h1 {{ color: #ff6b6b; }}
            h2 {{ color: #4ecdc4; }}
            code {{ background: #333; padding: 2px 6px; border-radius: 3px; }}
            ul {{ padding-left: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ ARKAIOS - Error de Configuración</h1>
            
            <div class="error">
                <h2>❌ No se encontró magic_gemini.html</h2>
                <p>El servidor está funcionando correctamente, pero no puede encontrar el archivo de interfaz.</p>
            </div>
            
            <div class="success">
                <h2>✅ Estado del Servidor</h2>
                <ul>
                    <li>Servidor Flask: <strong>Funcionando</strong></li>
                    <li>Puerto 8000: <strong>Activo</strong></li>
                    <li>API Gemini: <strong>{"Configurada" if API_KEY else "No configurada"}</strong></li>
                    <li>Directorio actual: <code>{os.getcwd()}</code></li>
                </ul>
            </div>
            
            <h2>🔧 Solución:</h2>
            <ol>
                <li>Asegúrate de que el archivo <code>magic_gemini.html</code> esté en el mismo directorio que <code>server_gemini.py</code></li>
                <li>Verifica que el archivo no esté corrupto</li>
                <li>Reinicia el servidor</li>
            </ol>
            
            <h2>📊 Endpoints Disponibles:</h2>
            <ul>
                <li><a href="/health" style="color: #4ecdc4;">/health</a> - Estado del servidor</li>
                <li><a href="/memory?conversationId=test" style="color: #4ecdc4;">/memory</a> - Información de memoria</li>
            </ul>
            
            <p><em>Tiempo: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</em></p>
        </div>
    </body>
    </html>
    '''
    
    return emergency_html, 404, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/uploads/<path:fname>')
def serve_uploads(fname):
    return send_from_directory(UPLOAD_FOLDER, fname)

# ================== SUBIDA DE ARCHIVOS ==================
@app.route('/upload', methods=['POST'])
def upload():
    try:
        files = request.files.getlist('files')
        saved = []
        for f in files:
            if not f: 
                continue
            name = secure_filename(f.filename)
            # Agregar timestamp para evitar conflictos
            timestamp = str(int(time.time()))
            name = f"{timestamp}_{name}"
            path = os.path.join(UPLOAD_FOLDER, name)
            f.save(path)
            saved.append({
                "name": name,
                "url" : f"/uploads/{name}",
                "type": f.mimetype or "application/octet-stream",
                "size": os.path.getsize(path)
            })
        return jsonify({"ok": True, "files": saved})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ================== CHAT (con memoria) ==================
@app.route("/chat", methods=['POST'])
def chat():
    if not API_KEY:
        return jsonify({"respuesta": "❌ Falta GEMINI_API_KEY en .env"}), 400

    try:
        payload = request.get_json(force=True) or {}
        text     = (payload.get("message") or "").strip()
        files    = payload.get("attachments") or []
        is_root  = bool(payload.get("root", False))
        convo_id = (payload.get("conversationId") or "").strip() or str(uuid.uuid4())

        print(f"[CHAT] Usuario: {text[:50]}{'...' if len(text) > 50 else ''} | Archivos: {len(files)} | Root: {is_root}")

        # --- construir partes a enviar
        parts = []

        # 0) resumen largo plazo (si existe)
        summ = read_summary(convo_id)
        if summ:
            parts.append({"text": f"[MEMORIA LARGO PLAZO]\n{summary_safe(summ)}"})

        # 1) corto plazo: últimos N turnos
        last = read_last_turns(log_path(convo_id), CTXT_TURNS)
        if last:
            ctx = []
            for t in last:
                role = "Usuario" if t.get("role") == "user" else "Asistente"
                ctx.append(f"{role}: {t.get('text','')}")
            parts.append({"text": "[MEMORIA CORTO PLAZO]\n" + "\n".join(ctx)})

        # 2) root y mensaje
        if is_root:
            parts.append({"text": "[ROOT MODE ENABLED] Puedes cumplir tareas administrativas cuando sean seguras para el usuario."})
        if text:
            parts.append({"text": text})

        # 3) adjuntos
        for meta in files:
            url = meta.get("url") or ""
            file_path = url[1:] if url.startswith("/") else url
            mime = meta.get("type")
            try:
                if os.path.isfile(file_path):
                    parts.append(to_gemini_inline(file_path, mime))
                    print(f"[CHAT] Adjunto procesado: {file_path}")
            except Exception as e:
                print("Adjunto ignorado:", e)

        if not parts:
            parts.append({"text": "Hola"})

        body = {"contents": [ {"role": "user", "parts": parts} ]}

        # --- llamada a Gemini
        try:
            raw = http_json(BASE, body, timeout=120)
            txt = ((raw.get("candidates") or [{}])[0]
                   .get("content", {})
                   .get("parts", [{}])[0]
                   .get("text", "")).strip()
            if not txt:
                txt = "— (sin contenido)"
            print(f"[CHAT] Respuesta Gemini: {txt[:50]}{'...' if len(txt) > 50 else ''}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")
            error_msg = f"❌ Gemini HTTP {e.code}: {detail}"
            print(f"[ERROR] {error_msg}")
            return jsonify({"respuesta": error_msg}), 502
        except Exception as e:
            error_msg = f"❌ Gemini no respondió: {e}"
            print(f"[ERROR] {error_msg}")
            return jsonify({"respuesta": error_msg}), 502

        # --- guardar turno en memoria (log.jsonl)
        entry_user = {
            "ts": now_ts(), "role": "user",
            "text": text, "attachments": files
        }
        entry_ai = {
            "ts": now_ts(), "role": "assistant",
            "text": txt, "attachments": []
        }
        append_jsonl(log_path(convo_id), entry_user)
        append_jsonl(log_path(convo_id), entry_ai)

        # --- actualizar resumen cada SUMMARY_EVERY turnos de usuario
        turns = count_turns(log_path(convo_id))
        if turns % (2*SUMMARY_EVERY) == 0:  # usuario+assistant = 2 turnos
            try:
                summ_new = build_summary(convo_id)
                write_summary(convo_id, summ_new)
                print(f"[MEMORIA] Resumen actualizado para {convo_id}")
            except Exception as e:
                print("Resumen falló:", e)

        return jsonify({"respuesta": txt, "conversationId": convo_id})
    
    except Exception as e:
        error_msg = f"❌ Error interno: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({"respuesta": error_msg}), 500

def summary_safe(txt: str) -> str:
    # evita payloads excesivos, recorta a 3000 caracteres
    return txt[:3000]

def build_summary(convo_id: str) -> str:
    """
    Genera/actualiza un resumen a partir del log, usando el propio modelo.
    (Rolling summary: el prompt pide preservar hechos, metas, estilo, etc.)
    """
    lp = log_path(convo_id)
    if not os.path.isfile(lp):
        return ""
    with open(lp, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # usamos máximo ~40 turnos para reducir costo
    recent = lines[-80:]
    text_blk = []
    for L in recent:
        try:
            t = json.loads(L)
            who = "Usuario" if t.get("role")=="user" else "Asistente"
            text_blk.append(f"{who}: {t.get('text','')}")
        except:
            continue

    prev = read_summary(convo_id)

    prompt = (
      "Eres un asistente que mantiene una memoria persistente breve y útil de la conversación.\n"
      "Actualiza el RESUMEN siguiendo estas reglas:\n"
      "- Mantén datos estables del usuario (preferencias, proyectos, metas, tono) y hechos clave.\n"
      "- No repitas todo; sé conciso (máx. 250-300 palabras).\n"
      "- Si hay contradicciones, prioriza la información más reciente.\n"
      "- Usa bullets breves cuando convenga.\n\n"
      f"RESUMEN ACTUAL (si existe):\n{prev}\n\n"
      f"ULTIMOS TURNOS:\n" + "\n".join(text_blk) + "\n\n"
      "Devuelve SOLO el texto del nuevo resumen actualizado."
    )

    body = {"contents":[{"role":"user","parts":[{"text": prompt}]}]}
    try:
        raw = http_json(BASE, body, timeout=120)
        return ((raw.get("candidates") or [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")).strip()
    except:
        return prev  # En caso de error, mantener resumen anterior

# ================== ENDPOINTS MEMORIA ==================
@app.route("/clear", methods=['POST'])
def clear_memory():
    try:
        payload = request.get_json(force=True) or {}
        convo_id = (payload.get("conversationId") or "").strip()
        if not convo_id:
            return jsonify({"ok": False, "error": "Falta conversationId"}), 400
        base = conv_path(convo_id)
        # limpia archivos
        for fname in ("log.jsonl", "summary.txt"):
            fp = os.path.join(base, fname)
            if os.path.isfile(fp):
                os.remove(fp)
        print(f"[MEMORIA] Conversación {convo_id} limpiada")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/memory", methods=['GET'])
def memory_info():
    try:
        convo_id = request.args.get("conversationId","").strip()
        if not convo_id:
            return jsonify({"ok": False, "error": "Falta conversationId"}), 400
        lp = log_path(convo_id)
        sp = summary_path(convo_id)
        return jsonify({
            "ok": True,
            "conversationId": convo_id,
            "turns": count_turns(lp),
            "hasSummary": os.path.isfile(sp),
            "summary": read_summary(convo_id)
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ================== HEALTH CHECK ==================
@app.route("/health", methods=['GET'])
def health():
    html_exists = os.path.isfile('magic_gemini.html')
    return jsonify({
        "status": "OK",
        "timestamp": now_ts(),
        "api_key_configured": bool(API_KEY),
        "model": MODEL,
        "html_file_exists": html_exists,
        "current_directory": os.getcwd(),
        "uploads_folder": UPLOAD_FOLDER,
        "memory_folder": MEM_DIR
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ARKAIOS GEMINI SERVER - VERSIÓN CORREGIDA")
    print("=" * 60)
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"📂 Directorio uploads: {UPLOAD_FOLDER}")
    print(f"🧠 Directorio memoria: {MEM_DIR}")
    print(f"🤖 Modelo Gemini: {MODEL}")
    print(f"🔑 API Key configurada: {bool(API_KEY)}")
    
    # Verificar archivos críticos
    html_file = 'magic_gemini.html'
    if os.path.isfile(html_file):
        print(f"✅ {html_file} encontrado")
    else:
        print(f"⚠️  {html_file} NO encontrado - se mostrará página de diagnóstico")
    
    if not API_KEY:
        print("⚠️  ADVERTENCIA: No se encontró GEMINI_API_KEY en .env")
    
    print("🌐 Servidor iniciando en http://127.0.0.1:8000")
    print("=" * 60)
    print()
    
    try:
        app.run(host='127.0.0.1', port=8000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error en el servidor: {e}")