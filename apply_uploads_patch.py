import os, re, time, sys

TARGET = "server_gemini_merged_root.py"
BACKUP = f"{TARGET}.bak_uploads_{int(time.time())}"

def read(p): 
    with open(p, "r", encoding="utf-8") as f: 
        return f.read()

def write(p, s): 
    with open(p, "w", encoding="utf-8") as f: 
        f.write(s)

def ensure_after(pattern, insertion, text, label):
    if insertion.strip() in text:
        print(f"[=] {label} ya presente, ok.")
        return text
    m = re.search(pattern, text, flags=re.DOTALL)
    if not m:
        print(f"[!] No se encontró ancla para {label}. Se insertará al inicio del archivo.")
        return insertion + "\n\n" + text
    idx = m.end()
    out = text[:idx] + "\n\n" + insertion + "\n" + text[idx:]
    print(f"[+] Insertado: {label}")
    return out

def ensure_route(pattern_def, text, label):
    if re.search(pattern_def, text, flags=re.DOTALL):
        print(f"[=] {label} ya existe, ok.")
        return text
    # Inserta antes de if __name__ == '__main__':
    anchor = re.search(r"\nif\s+__name__\s*==\s*['\"]__main__['\"]\s*:", text)
    block = {
"serve_upload": '''
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)
''',

"verify_file_is_image": r'''
# -------- Utilidad: verificación básica de imagen ----------
def verify_file_is_image(path: str, min_bytes: int = 16) -> tuple[bool, str]:
    try:
        if (not os.path.exists(path)) or (os.path.getsize(path) < min_bytes):
            return False, "archivo no existe o está vacío"
        from PIL import Image as _PIL_Image
        with _PIL_Image.open(path) as im:
            im.verify()
        return True, ""
    except Exception as e:
        return False, str(e)
''',

"upload_endpoint": r'''
# -------- Endpoint: subida de archivos de usuario (multipart) ----------
@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    if not f or not f.filename:
        return jsonify({"ok": False, "error": "archivo requerido"}), 400
    fname = secure_filename(f.filename)
    bad_ext = {'.exe', '.js', '.bat', '.cmd', '.sh'}
    _, ext = os.path.splitext(fname.lower())
    if ext in bad_ext:
        return jsonify({"ok": False, "error": f"extensión no permitida: {ext}"}), 400
    path = os.path.join(USR_DIR, f"{int(time.time())}_{fname}")
    f.save(path)
    url = f"/uploads/{os.path.relpath(path, UPLOAD_FOLDER).replace(os.sep,'/')}"
    return jsonify({"ok": True, "url": url, "name": fname, "type": "application/octet-stream"})
''',

"cleanup_uploads": r'''
# -------- Limpieza automática (TTL en horas) ----------
def cleanup_uploads(ttl_hours=24):
    cutoff = time.time() - ttl_hours*3600
    for root in (GEN_DIR, THREED_DIR, USR_DIR):
        try:
            for n in os.listdir(root):
                p = os.path.join(root, n)
                if os.path.isfile(p) and os.path.getmtime(p) < cutoff:
                    os.remove(p)
        except Exception:
            pass
'''
    }
    ins = block[label]
    if anchor:
        i = anchor.start()
        out = text[:i] + "\n\n" + ins + "\n" + text[i:]
    else:
        out = text + "\n\n" + ins + "\n"
    print(f"[+] Insertado: {label}")
    return out

def main():
    if not os.path.exists(TARGET):
        print(f"[x] No existe {TARGET} en esta carpeta.")
        sys.exit(1)

    txt = read(TARGET)
    write(BACKUP, txt)
    print(f"[*] Backup creado: {BACKUP}")

    # 1) MAX_CONTENT_LENGTH y subcarpetas (después de crear app y UPLOAD_FOLDER)
    pattern_app = r"app\s*=\s*Flask\([^\)]*\)[\s\S]*?os\.makedirs\(MEM_DIR,\s*exist_ok=True\)"
    insertion_app = r'''
# Tamaño máximo de subida (20 MB)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

# Subcarpetas para organización:
GEN_DIR = os.path.join(UPLOAD_FOLDER, "generated")
USR_DIR = os.path.join(UPLOAD_FOLDER, "user")
THREED_DIR = os.path.join(UPLOAD_FOLDER, "three_d")
for _d in (GEN_DIR, USR_DIR, THREED_DIR):
    os.makedirs(_d, exist_ok=True)
'''.strip()
    txt = ensure_after(pattern_app, insertion_app, txt, "MAX_CONTENT_LENGTH + subcarpetas")

    # 2) Ruta /uploads/<path>
    txt = ensure_route(r"@app\.route\('/uploads/<path:filename>'\)", txt, "serve_upload")

    # 3) Utilidad verify_file_is_image
    if "def verify_file_is_image(" not in txt:
        txt = ensure_route(r"def verify_file_is_image\(", txt, "verify_file_is_image")

    # 4) Cambiar salida por defecto de generate_image_with_ai a GEN_DIR
    txt_new = re.sub(
        r"output_path\s*=\s*os\.path\.join\(\s*UPLOAD_FOLDER\s*,\s*f?[\"']generated_\{int\(time\.time\(\)\)\}\.png[\"']\s*\)",
        "output_path = os.path.join(GEN_DIR, f\"generated_{int(time.time())}.png\")",
        txt
    )
    if txt_new != txt:
        print("[+] generate_image_with_ai() ahora guarda en GEN_DIR")
        txt = txt_new
    else:
        print("[=] generate_image_with_ai() ya estaba apuntando a GEN_DIR (o no se encontró patrón).")

    # 5) En /chat: verificar y adjuntar URL relativa
    chat_pat = r"@app\.route\('/chat',\s*methods=\['POST'\]\)\s*def\s+chat\(\):"
    m = re.search(chat_pat, txt)
    if not m:
        print("[!] No encontré la función /chat; no se pudo parchear esa parte.")
    else:
        # Inserta verificación justo después de donde se asigna image_path
        block_verify = r'''
                    # Verificación de integridad antes de adjuntar
                    ok_img, why_img = verify_file_is_image(image_path)
                    if not ok_img:
                        txt += f"\n\n❌ Imagen generada pero inválida: {why_img}"
                    else:
                        rel = os.path.relpath(image_path, UPLOAD_FOLDER).replace(os.sep, '/')
                        image_url = f"/uploads/{rel}"
                        generated_images.append(image_url)
                        txt += f"\n\n✅ Imagen generada\nURL: {image_url}\nPrompt: {enhanced}"
'''.rstrip("\n")

        # Solo inserta si no existe ya
        if "Verificación de integridad antes de adjuntar" not in txt:
            # Buscar la línea "image_path = ..." dentro de chat()
            chat_body_start = m.end()
            chat_body_end = re.search(r"\n\S", txt[chat_body_start:])  # aproximado
            search_range = txt[chat_body_start:]
            mp = re.search(r"image_path\s*=\s*generate_image_(with_ai|locally)\([^\)]*\)\s*", search_range)
            if mp:
                ins_idx = chat_body_start + mp.end()
                txt = txt[:ins_idx] + block_verify + txt[ins_idx:]
                print("[+] Añadido bloque de verificación en /chat")
            else:
                print("[=] No encontré asignación a image_path dentro de /chat; salto ese añadido.")
        else:
            print("[=] Verificación ya existente en /chat")

    # 6) Endpoint /upload
    txt = ensure_route(r"@app\.route\('/upload',\s*methods=\['POST'\]\)", txt, "upload_endpoint")

    # 7) cleanup_uploads
    if "def cleanup_uploads(" not in txt:
        txt = ensure_route(r"def cleanup_uploads\(", txt, "cleanup_uploads")
    else:
        print("[=] cleanup_uploads ya está.")

    write(TARGET, txt)
    print("[✔] Parche aplicado a server_gemini_merged_root.py")

if __name__ == "__main__":
    main()
