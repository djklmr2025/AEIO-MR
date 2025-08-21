import os
import time
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from openai import OpenAI

# ============================
# Cargar clave API de OpenAI
# ============================
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ No se encontró la clave API en el archivo .env")

client = OpenAI(api_key=api_key)

# ============================
# Configuración Flask
# ============================
app = Flask(__name__, static_folder=".", static_url_path="")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

conversation_history = []

@app.route("/")
def home():
    return send_from_directory(".", "magic.html")

# ============================
# Endpoint de Chat (MEJORADO)
# ============================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json or {}
        user_message = data.get("mensaje", "").strip()
        attachments = data.get("attachments", [])

        # Construir mensaje con información de archivos
        if attachments:
            files_info = "\n".join([f"📁 Archivo adjunto: {att['name']} ({att['type']})" for att in attachments])
            user_message = f"{user_message}\n\n{files_info}" if user_message else files_info

        if not user_message:
            return jsonify({"error": "No se recibió contenido válido"}), 400

        conversation_history.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Eres Arkaios, un asistente útil que puede analizar archivos adjuntos."}
            ] + conversation_history
        )

        bot_reply = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": bot_reply})

        return jsonify({"respuesta": bot_reply})

    except Exception as e:
        return jsonify({"respuesta": f"❌ Error al conectar con OpenAI: {str(e)}"}), 500

# ============================
# Limpiar memoria
# ============================
@app.route("/clear", methods=["POST"])
def clear():
    conversation_history.clear()
    return jsonify({"status": "Memoria borrada"})

# ============================
# Subida de archivos (MEJORADO)
# ============================
@app.route("/upload", methods=["POST"])
def upload_files():
    if "files" not in request.files:
        return jsonify({"error": "No se enviaron archivos"}), 400

    files = request.files.getlist("files")
    saved_files = []

    for file in files:
        try:
            # Aceptar cualquier tipo de archivo
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            saved_files.append({
                "name": filename,
                "url": f"/uploads/{filename}",
                "type": file.mimetype,
                "size": os.path.getsize(filepath)
            })
        except Exception as e:
            return jsonify({"error": f"Error procesando {file.filename}: {str(e)}"}), 500

    return jsonify({"files": saved_files}), 200

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ============================
# Validación de conexión
# ============================
def validar_conexion():
    print("🔄 Verificando conexión con OpenAI...")
    try:
        inicio = time.time()
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Solo responde con la palabra: OK"}]
        )
        duracion = round((time.time() - inicio) * 1000)
        print(f"✅ Arkaios conectado con OpenAI correctamente.")
        print(f"🆔 ID de sesión: {resp.id}")
        print(f"⏱ Tiempo de respuesta: {duracion} ms\n")
    except Exception as e:
        print(f"❌ Error en la conexión con OpenAI: {e}")
        exit(1)

# ============================
# Arranque seguro en localhost
# ============================
if __name__ == "__main__":
    validar_conexion()
    app.run(host="127.0.0.1", port=8000, debug=False)