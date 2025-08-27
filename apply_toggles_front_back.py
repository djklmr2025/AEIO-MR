import os, re, time

SERVER="server_gemini_merged_root.py"
MAGIC="magic.html"

def rd(p): return open(p,'r',encoding='utf-8').read()
def wr(p,s): open(p,'w',encoding='utf-8').write(s)

def patch_magic():
    s=rd(MAGIC); bak=f"{MAGIC}.bak_{int(time.time())}"; wr(bak,s)
    # Panel de toggles (si no existe)
    if 'id="feature-toggles"' not in s:
        s=re.sub(r"(<body[^>]*>)", r"""\1
  <div id="feature-toggles" class="toggle-row">
    <label><input type="checkbox" id="toggle-image" checked> Imagen (HF)</label>
    <label><input type="checkbox" id="toggle-3d"> 3D (Hunyuan)</label>
    <label><input type="checkbox" id="toggle-web"> Búsqueda Web</label>
    <label><input type="checkbox" id="toggle-memory" checked> Memoria</label>
  </div>
""", s, count=1, flags=re.IGNORECASE)
    # Estilos
    if "toggle-row" not in s:
        s=re.sub(r"</head>", """
  <style>.toggle-row{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:10px 0 6px}
  .toggle-row label{display:flex;align-items:center;gap:6px;font:14px/1.3 system-ui,Arial}</style>
</head>""", s, count=1)
    # Helpers + envío de features
    if "readFeatureFlags" not in s:
        s=re.sub(r"</script>", """
  function readFeatureFlags(){return{image:document.getElementById('toggle-image')?.checked??true,threeD:document.getElementById('toggle-3d')?.checked??false,web:document.getElementById('toggle-web')?.checked??false,memory:document.getElementById('toggle-memory')?.checked??true};}
  function loadFeatureFlags(){try{const f=JSON.parse(localStorage.getItem('arkaios:flags')||'{}');if('image'in f)document.getElementById('toggle-image').checked=!!f.image;if('threeD'in f)document.getElementById('toggle-3d').checked=!!f.threeD;if('web'in f)document.getElementById('toggle-web').checked=!!f.web;if('memory'in f)document.getElementById('toggle-memory').checked=!!f.memory;}catch{}}
  function saveFeatureFlags(){localStorage.setItem('arkaios:flags',JSON.stringify(readFeatureFlags()));}
  document.addEventListener('DOMContentLoaded',loadFeatureFlags);
  ['toggle-image','toggle-3d','toggle-web','toggle-memory'].forEach(id=>{document.addEventListener('change',e=>{if(e.target&&e.target.id===id)saveFeatureFlags();});});
</script>""", s, count=1)
    # Inyectar features al fetch('/chat')
    if "features" not in s:
        s=re.sub(r"body:\s*JSON\.stringify\(\{([^}]*)\}\)",
                 r"body: JSON.stringify({\1, features: readFeatureFlags() })", s, count=1)
    # Asegurar render de generatedImages
    if "generatedImages" not in s or "attachments" not in s:
        s=re.sub(r"addMessage\(\{[^}]*who\s*:\s*['\"]ai['\"][^}]*\}\);",
                 "const genImgs=(data.generatedImages||[]).map(url=>({name:url.split('/').pop(),url,type:'image/png'}));\n    const allAtt=[...(uploaded||[]),...genImgs];\n    addMessage({ text:data.respuesta||'(sin respuesta)', who:'ai', attachments: allAtt });",
                 s, count=1)
    wr(MAGIC,s); print("[magic.html] aplicado. Backup:",bak)

def patch_server():
    s=rd(SERVER); bak=f"{SERVER}.bak_{int(time.time())}"; wr(bak,s)
    # Subcarpetas + límite + /uploads
    if "GEN_DIR" not in s:
        s=s.replace("os.makedirs(MEM_DIR, exist_ok=True)", """os.makedirs(MEM_DIR, exist_ok=True)
GEN_DIR=os.path.join(UPLOAD_FOLDER,'generated')
USR_DIR=os.path.join(UPLOAD_FOLDER,'user')
THREED_DIR=os.path.join(UPLOAD_FOLDER,'three_d')
for _d in (GEN_DIR,USR_DIR,THREED_DIR): os.makedirs(_d, exist_ok=True)
app.config['MAX_CONTENT_LENGTH']=20*1024*1024
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)
def verify_file_is_image(path,min_bytes=16):
    try:
        if (not os.path.exists(path)) or (os.path.getsize(path)<min_bytes): return (False,'archivo no existe o está vacío')
        from PIL import Image as _PIL_Image
        with _PIL_Image.open(path) as im: im.verify()
        return (True,'')
    except Exception as e:
        return (False,str(e))
""")
    # Guardar imágenes en GEN_DIR
    s=re.sub(r"os\.path\.join\(\s*UPLOAD_FOLDER\s*,\s*f[\"']generated_\{int\(time\.time\(\)\)\}\.png[\"']\s*\)",
             "os.path.join(GEN_DIR, f\"generated_{int(time.time())}.png\")", s)
    # Leer toggles y condicionar imagen
    if "features = data.get(\"features\")" not in s:
        s=s.replace('message = data.get("message", "").strip()',
                    'message = data.get("message", "").strip()\n        features = data.get("features") or {}\n        use_image  = bool(features.get("image", True))\n        use_threeD = bool(features.get("threeD", False))\n        use_web    = bool(features.get("web", False))\n        use_memory = bool(features.get("memory", True))')
    s=s.replace("if IMAGE_GENERATION_ENABLED:", "if IMAGE_GENERATION_ENABLED and use_image:")
    # Anti-apelativos (pero mantenemos el vibe si te gusta: quítalo si no lo quieres)
    if "cariño" not in s:
        s=s.replace("return jsonify({", 
                    "for bad in ['cariño','mi amor','bebé']:\n            respuesta = re.sub(rf\"\\b{bad}\\b\",\"\", respuesta, flags=re.IGNORECASE)\n        return jsonify({", 1)
    wr(SERVER,s); print("[server] aplicado. Backup:",bak)

if __name__=='__main__':
    if not (os.path.exists(SERVER) and os.path.exists(MAGIC)):
        print("Ejecuta este script desde la raíz del repo, donde están server_gemini_merged_root.py y magic.html")
    else:
        patch_magic(); patch_server(); print("✔ Listo.")
