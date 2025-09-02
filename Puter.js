<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>Arkaios UI — Claude con Puter.js</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="icon" href="https://img.icons8.com/fluency/48/robot-2.png" />
  <!-- SDK de Puter -->
  <script src="https://js.puter.com/v2/"></script>
  <style>
    :root{--bg:#091017;--surface:#0d1a28;--ink:#e6f1ff;--muted:#9fb4d3;--brand:#7c4dff;--accent:#b388ff;--danger:#ff5b8a;--line:#14314f}
    *{box-sizing:border-box} html,body{height:100%}
    body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto;background:var(--bg);color:var(--ink)}
    .wrap{max-width:1100px;margin:0 auto;padding:16px;display:flex;flex-direction:column;height:100%}
    header{display:flex;align-items:center;gap:12px;margin-bottom:12px}
    header h1{font-size:20px;margin:0}
    .badge{font-size:12px;padding:4px 8px;border-radius:999px;background:#0e253e;border:1px solid var(--line);color:#bfe2ff}
    .status{font-size:11px;padding:2px 6px;border-radius:12px;margin-left:8px}
    .status.online{background:#004225;color:#00e1a3;border:1px solid #006b3d}
    .status.offline{background:#3d1a1a;color:#ff5b8a;border:1px solid #5c2929}
    .status.connecting{background:#3d3d1a;color:#e1e100;border:1px solid #5c5c29}
    #history{flex:1;overflow:auto;border:1px solid var(--line);border-radius:12px;padding:14px;background:rgba(255,255,255,.03)}
    .msg{padding:12px;border-radius:12px;margin-bottom:12px;opacity:0;animation:fadeIn .3s forwards}
    .msg.user{background:rgba(0,225,163,.14);border:1px solid rgba(0,225,163,.35);margin-left:15%}
    .msg.ai{background:rgba(124,77,255,.12);border:1px solid rgba(124,77,255,.35);margin-right:15%}
    .msg.ai .tools{margin-top:8px;display:flex;gap:8px}
    .msg.root{background:rgba(255,91,138,.12);border:1px solid rgba(255,91,138,.35)}
    .msg.system{background:rgba(255,193,7,.1);border:1px solid rgba(255,193,7,.3);text-align:center}
    .head{font-size:12px;color:var(--muted);margin-bottom:6px}
    .content{white-space:pre-wrap;line-height:1.6}
    .attachments{margin-top:8px;border-top:1px dashed var(--line);padding-top:8px;display:flex;flex-wrap:wrap;gap:8px}
    .thumb{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);padding:6px;border-radius:8px;background:var(--surface)}
    .thumb img{max-width:160px;max-height:110px;border-radius:6px;display:block}
    .panel{margin-top:12px;border:1px solid var(--line);background:var(--surface);border-radius:12px;padding:12px}
    textarea{width:100%;min-height:90px;resize:none;background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:10px;padding:12px;color:var(--ink)}
    textarea:focus{outline:none;border-color:var(--brand)}
    .row{display:flex;gap:8px;align-items:center;justify-content:space-between;margin-top:8px}
    .btn{cursor:pointer;border-radius:10px;padding:10px 14px;border:1px solid var(--line);background:transparent;color:var(--ink);font-size:13px;transition:all .2s}
    .btn:hover{border-color:var(--brand);background:rgba(124,77,255,.1)}
    .btn:disabled{opacity:.5;cursor:not-allowed}
    .btn.primary{background:var(--brand);color:#ffffff;border:none;font-weight:600}
    .btn.primary:hover{background:#6b3fe0}
    .btn.warning{border-color:#ff9db8;color:#ffd0dd}
    .filebar{display:flex;gap:10px;align-items:center;margin-top:8px;flex-wrap:wrap}
    .previews{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}
    .drop{border:2px dashed var(--line);border-radius:10px;padding:12px;color:var(--muted);text-align:center;transition:border-color .2s}
    .drop.dragover{border-color:var(--brand);background:rgba(124,77,255,.05)}
    .right{margin-left:auto}
    .switch{display:inline-flex;align-items:center;gap:8px;background:#15283f;border:1px solid var(--line);padding:6px 10px;border-radius:999px}
    .hint{font-size:12px;color:var(--muted)}
    .model-selector {background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 8px 12px; color: var(--ink);}
    @keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>ARKAIOS UI</h1>
      <span class="badge">Puter.js + Claude</span>
      <span class="status connecting" id="connectionStatus">Conectando...</span>
      <select class="model-selector" id="modelSelector">
        <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
        <option value="claude-3-opus">Claude 3 Opus</option>
        <option value="claude-3-haiku">Claude 3 Haiku</option>
      </select>
    </header>

    <main id="history"></main>

    <section class="panel">
      <div class="filebar">
        <input type="file" id="fileInput" multiple accept="image/*,application/pdf,.pdf,.txt,.md,.json" />
        <button class="btn" id="clearBtn" title="Quitar adjuntos">Limpiar adjuntos</button>
        <div class="drop" id="drop">Arrastra y suelta archivos aquí… o pega con Ctrl+V</div>
      </div>
      <div class="previews" id="previews"></div>

      <textarea id="prompt" placeholder="Escribe tu mensaje… (Ej: 'Explícame la computación cuántica')" maxlength="4000"></textarea>
      <div class="row">
        <div>
          <button class="btn" id="cleanChat">Limpiar chat</button>
          <button class="btn warning" id="pingBtn">Probar conexión</button>
        </div>
        <button class="btn primary" id="sendBtn">Enviar</button>
      </div>
    </section>
  </div>

  <script>
    // Variables globales
    const historyDiv = document.getElementById('history');
    const input = document.getElementById('prompt');
    const fileInput = document.getElementById('fileInput');
    const previews = document.getElementById('previews');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearBtn');
    const pingBtn = document.getElementById('pingBtn');
    const cleanChatBtn = document.getElementById('cleanChat');
    const statusEl = document.getElementById('connectionStatus');
    const modelSelector = document.getElementById('modelSelector');
    
    let pendingFiles = [];
    let isConnected = false;
    let conversationHistory = [];
    let puterReady = false;
    let initRetries = 0;
    const maxRetries = 15;

    // Esperar a que Puter.js se cargue
    async function waitForPuter() {
      while (initRetries < maxRetries) {
        if (typeof puter !== 'undefined' && puter?.ai) {
          puterReady = true;
          return true;
        }
        initRetries++;
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      return false;
    }

    // Funciones de estado de conexión - CORREGIDAS
    function updateConnectionStatus(ok) { 
      isConnected = ok; 
      statusEl.textContent = ok ? 'Conectado' : 'Error'; 
      statusEl.className = 'status ' + (ok ? 'online' : 'offline'); 
    }
    
    function setConnecting() { 
      statusEl.textContent = 'Conectando...'; 
      statusEl.className = 'status connecting'; 
    }

    // Añadir mensaje al historial - MEJORADO
    function addMessage({text, who = 'ai', attachments = [], isSystem = false}) {
      const wrap = document.createElement('div');
      let cls = `msg ${who}`; 
      if (isSystem) cls += ' system';
      wrap.className = cls;

      const head = document.createElement('div');
      head.className = 'head';
      head.textContent = isSystem ? 'Sistema' : (who === 'user' ? 'Tú' : 'Arkaios (Claude)');

      const body = document.createElement('div');
      body.className = 'content';
      body.textContent = text;

      wrap.appendChild(head);
      wrap.appendChild(body);

      // Botón para guardar respuesta - MEJORADO
      if (who === 'ai' && !isSystem && text.length > 50) {
        const tools = document.createElement('div');
        tools.className = 'tools';
        const saveBtn = document.createElement('button');
        saveBtn.className = 'btn';
        saveBtn.textContent = 'Guardar (.txt)';
        saveBtn.onclick = () => {
          const timestamp = new Date().toISOString().replace(/:/g, '-').split('.')[0];
          const content = `ARKAIOS - Respuesta de Claude
Timestamp: ${new Date().toLocaleString()}
Modelo: ${modelSelector.value}

${text}`;
          const blob = new Blob([content], {type: 'text/plain;charset=utf-8'});
          const a = document.createElement('a');
          a.href = URL.createObjectURL(blob);
          a.download = `arkaios-claude-${timestamp}.txt`;
          a.click();
          URL.revokeObjectURL(a.href);
        };
        tools.appendChild(saveBtn);
        wrap.appendChild(tools);
      }

      // Mostrar archivos adjuntos - MEJORADO
      if (attachments?.length) {
        const att = document.createElement('div'); 
        att.className = 'attachments';
        attachments.forEach(a => {
          const box = document.createElement('div'); 
          box.className = 'thumb';
          if (a.type?.startsWith('image/')) {
            const img = new Image(); 
            img.alt = a.name; 
            img.src = a.preview || a.url;
            img.onerror = () => {
              img.style.display = 'none';
              const span = document.createElement('span');
              span.textContent = '❌ ' + a.name;
              box.appendChild(span);
            };
            box.appendChild(img);
          } else {
            const s = document.createElement('span'); 
            s.textContent = '📄 ' + (a.name || a.url); 
            box.appendChild(s);
          }
          att.appendChild(box);
        });
        wrap.appendChild(att);
      }

      historyDiv.appendChild(wrap);
      historyDiv.scrollTop = historyDiv.scrollHeight;
      return wrap;
    }

    // Previsualizaciones - CORREGIDAS
    function renderPreviews() {
      previews.innerHTML = '';
      pendingFiles.forEach((f, idx) => {
        const box = document.createElement('div'); 
        box.className = 'thumb'; 
        box.style.position = 'relative';
        
        const x = document.createElement('button'); 
        x.textContent = '×';
        x.style.cssText = 'position:absolute;top:-8px;right:-8px;width:20px;height:20px;border-radius:50%;background:var(--danger);color:#fff;border:none;cursor:pointer;font-size:12px;line-height:1;z-index:1';
        x.onclick = () => { 
          URL.revokeObjectURL(pendingFiles[idx].preview); // Limpiar URL objeto
          pendingFiles.splice(idx, 1); 
          renderPreviews(); 
        };

        if (f.type.startsWith('image/')) {
          const img = new Image(); 
          img.alt = f.name; 
          img.style.maxWidth = '100px'; 
          img.style.maxHeight = '100px';
          img.style.objectFit = 'cover';
          box.appendChild(img);
          
          const rd = new FileReader(); 
          rd.onload = e => {
            img.src = e.target.result;
            f.preview = e.target.result; // Guardar para uso posterior
          };
          rd.onerror = () => {
            img.style.display = 'none';
            const span = document.createElement('span');
            span.textContent = '❌ Error';
            box.appendChild(span);
          };
          rd.readAsDataURL(f);
        } else {
          const s = document.createElement('span'); 
          s.textContent = '📄 ' + f.name; 
          s.style.maxWidth = '120px'; 
          s.style.overflow = 'hidden'; 
          s.style.textOverflow = 'ellipsis'; 
          s.style.whiteSpace = 'nowrap'; 
          box.appendChild(s);
        }
        
        box.appendChild(x); 
        previews.appendChild(box);
      });
    }

    // Manejo de archivos - CORREGIDO
    fileInput.addEventListener('change', e => {
      const newFiles = Array.from(e.target.files).filter(f => {
        if (f.size > 10 * 1024 * 1024) {
          addMessage({
            text: `Archivo ${f.name} omitido (>10MB)`, 
            who: 'ai', 
            isSystem: true
          });
          return false;
        }
        return true;
      });
      
      pendingFiles = [...pendingFiles, ...newFiles]; 
      renderPreviews(); 
      e.target.value = '';
    });
    
    clearBtn.addEventListener('click', () => { 
      // Limpiar URLs objeto para evitar memory leaks
      pendingFiles.forEach(f => {
        if (f.preview) URL.revokeObjectURL(f.preview);
      });
      pendingFiles = []; 
      renderPreviews(); 
      fileInput.value = ''; 
    });

    // Drag & Drop - MEJORADO
    const drop = document.getElementById('drop');
    
    ['dragenter', 'dragover'].forEach(ev => { 
      drop.addEventListener(ev, e => { 
        e.preventDefault(); 
        drop.classList.add('dragover'); 
      }); 
      document.addEventListener(ev, e => e.preventDefault()); 
    });
    
    ['dragleave', 'drop'].forEach(ev => { 
      drop.addEventListener(ev, e => { 
        e.preventDefault(); 
        drop.classList.remove('dragover'); 
      }); 
    });
    
    drop.addEventListener('drop', e => { 
      const newFiles = Array.from(e.dataTransfer.files).filter(f => {
        if (f.size > 10 * 1024 * 1024) {
          addMessage({
            text: `Archivo ${f.name} omitido (>10MB)`, 
            who: 'ai', 
            isSystem: true
          });
          return false;
        }
        return true;
      });
      
      pendingFiles = [...pendingFiles, ...newFiles]; 
      renderPreviews();
    });

    // Pegar imágenes - MEJORADO
    document.addEventListener('paste', async (e) => {
      const items = e.clipboardData?.items || [];
      let found = false;
      
      for (const it of items) {
        if (it.type && it.type.startsWith('image/')) {
          const blob = it.getAsFile();
          if (blob) {
            const file = new File([blob], `captura-${Date.now()}.png`, {type: blob.type});
            pendingFiles.push(file);
            found = true;
          }
        }
      }
      
      if (found) { 
        renderPreviews(); 
        addMessage({
          text: 'Imagen añadida desde portapapeles', 
          who: 'ai', 
          isSystem: true
        }); 
      }
    });

    // Subir archivos a Puter - COMPLETAMENTE CORREGIDO
    async function uploadFilesToPuter() {
      if (!pendingFiles.length) return [];
      if (!puterReady || !window.puter?.fs) {
        addMessage({
          text: 'Sistema de archivos no disponible. Archivos conservados localmente.',
          who: 'ai',
          isSystem: true
        });
        return pendingFiles.map(f => ({
          name: f.name,
          type: f.type,
          preview: f.preview,
          local: true
        }));
      }
      
      const uploadedFiles = [];
      
      for (const file of pendingFiles) {
        try {
          // Método 1: puter.fs.upload (si existe)
          let puterFile;
          let publicURL;
          
          if (puter.fs.upload) {
            puterFile = await puter.fs.upload(file);
            publicURL = await puter.fs.getPublicURL(puterFile.path);
          } else {
            // Método 2: puter.fs.write manual
            const safeName = file.name.replace(/[^\w\.-]/g, '_');
            const path = `/home/${safeName}`;
            
            const arrayBuffer = await file.arrayBuffer();
            const uint8Array = new Uint8Array(arrayBuffer);
            
            await puter.fs.write(path, uint8Array);
            puterFile = { path: path };
            
            // Intentar obtener URL pública
            try {
              publicURL = await puter.fs.getPublicURL(path);
            } catch {
              publicURL = path; // Fallback a path local
            }
          }
          
          uploadedFiles.push({
            name: file.name,
            url: publicURL,
            type: file.type,
            path: puterFile.path,
            preview: file.type.startsWith('image/') ? (file.preview || URL.createObjectURL(file)) : null
          });
          
        } catch (error) {
          console.error('Error subiendo archivo:', file.name, error);
          addMessage({
            text: `Error subiendo ${file.name}: ${error.message}`,
            who: 'ai', 
            isSystem: true
          });
          
          // Conservar archivo localmente
          uploadedFiles.push({
            name: file.name,
            type: file.type,
            preview: file.preview,
            local: true,
            error: error.message
          });
        }
      }
      
      return uploadedFiles;
    }

    // Función principal para enviar - COMPLETAMENTE CORREGIDA
    async function send() {
      const text = input.value.trim();
      if (!text && pendingFiles.length === 0) return;
      if (sendBtn.disabled) return;

      // Verificar que Puter está listo
      if (!puterReady) {
        addMessage({
          text: 'Sistema no listo. Verifica conexión con Puter.js.',
          who: 'ai',
          isSystem: true
        });
        return;
      }

      // Generar previsualizaciones locales
      const localPreview = [];
      for (const f of pendingFiles) {
        if (f.type.startsWith('image/')) {
          try {
            const preview = await new Promise((resolve, reject) => {
              const rd = new FileReader();
              rd.onload = e => resolve(e.target.result);
              rd.onerror = () => reject(new Error('Error leyendo archivo'));
              rd.readAsDataURL(f);
            });
            localPreview.push({name: f.name, preview: preview, type: f.type});
          } catch (err) {
            localPreview.push({name: f.name, type: f.type, error: err.message});
          }
        } else { 
          localPreview.push({name: f.name, type: f.type}); 
        }
      }
      
      // Mostrar mensaje del usuario
      if (text || localPreview.length) {
        addMessage({
          text: text || '(enviando adjuntos)', 
          who: 'user', 
          attachments: localPreview
        });
      }
      
      // Limpiar input y deshabilitar envío
      input.value = '';
      sendBtn.disabled = true;
      sendBtn.textContent = 'Enviando…';

      try {
        // 1. Subir archivos a Puter
        const uploadedFiles = await uploadFilesToPuter();
        
        // 2. Construir mensaje completo para Claude
        let fullMessage = text;
        
        if (uploadedFiles.length > 0) {
          fullMessage += "\n\nArchivos adjuntos:";
          uploadedFiles.forEach(file => {
            if (file.local) {
              fullMessage += `\n- ${file.name} (local, tipo: ${file.type})`;
            } else {
              fullMessage += `\n- ${file.name}: ${file.url || file.path}`;
            }
          });
        }
        
        // 3. Añadir al historial de conversación
        conversationHistory.push({ role: "user", content: fullMessage });
        
        // 4. Seleccionar modelo
        const selectedModel = modelSelector.value;
        
        // 5. Enviar mensaje a Claude - CON MÚLTIPLES FALLBACKS
        let aiResponse;
        
        try {
          // Método principal: puter.ai.chat
          if (puter?.ai?.chat) {
            console.log('Enviando a Claude via puter.ai.chat, modelo:', selectedModel);
            const response = await puter.ai.chat(fullMessage, {
              model: selectedModel,
              stream: false
            });
            
            // Procesar respuesta de Claude (múltiples formatos)
            if (typeof response === 'string') {
              aiResponse = response;
            } else if (response?.message?.content) {
              if (Array.isArray(response.message.content)) {
                aiResponse = response.message.content[0]?.text || response.message.content[0] || 'Respuesta vacía';
              } else {
                aiResponse = response.message.content;
              }
            } else if (response?.text) {
              aiResponse = response.text;
            } else if (response?.choices?.[0]?.message?.content) {
              aiResponse = response.choices[0].message.content;
            } else {
              aiResponse = 'Respuesta recibida en formato inesperado: ' + JSON.stringify(response).substring(0, 200);
            }
          } else {
            throw new Error('Método puter.ai.chat no disponible');
          }
        } catch (chatError) {
          console.warn('Error en chat principal:', chatError);
          
          // Fallback: intentar con complete
          if (puter?.ai?.complete) {
            console.log('Intentando fallback con puter.ai.complete');
            const completeResponse = await puter.ai.complete(fullMessage, {model: selectedModel});
            aiResponse = typeof completeResponse === 'string' ? 
              completeResponse : 
              (completeResponse?.text || JSON.stringify(completeResponse));
          } else {
            throw chatError;
          }
        }
        
        // 6. Validar respuesta
        if (!aiResponse || aiResponse.trim().length === 0) {
          aiResponse = 'Respuesta vacía recibida del modelo ' + selectedModel;
        }
        
        // 7. Añadir al historial
        conversationHistory.push({ role: "assistant", content: aiResponse });
        
        // 8. Mostrar respuesta
        updateConnectionStatus(true);
        addMessage({
          text: aiResponse,
          who: 'ai',
          attachments: uploadedFiles.filter(f => !f.error)
        });

        // 9. Mostrar errores si los hay
        const errorFiles = uploadedFiles.filter(f => f.error);
        if (errorFiles.length > 0) {
          addMessage({
            text: `Errores en ${errorFiles.length} archivo(s): ${errorFiles.map(f => f.name).join(', ')}`,
            who: 'ai',
            isSystem: true
          });
        }

      } catch (error) {
        console.error('Error completo en send():', error);
        updateConnectionStatus(false);
        addMessage({
          text: 'Error enviando mensaje: ' + (error.message || 'Error desconocido') + 
                '\n\nVerifica tu conexión con Puter.js y el modelo seleccionado.',
          who: 'ai', 
          isSystem: true
        });
      } finally {
        // Rehabilitar interfaz
        sendBtn.disabled = false;
        sendBtn.textContent = 'Enviar';
        
        // Limpiar archivos pendientes
        pendingFiles.forEach(f => {
          if (f.preview) URL.revokeObjectURL(f.preview);
        });
        pendingFiles = [];
        renderPreviews();
        fileInput.value = '';
      }
    }

    // Limpiar chat - MEJORADO
    cleanChatBtn.addEventListener('click', () => {
      if (!confirm('¿Borrar historial de conversación? Esta acción no se puede deshacer.')) return;
      
      historyDiv.innerHTML = '';
      conversationHistory = [];
      addMessage({
        text: 'Conversación reiniciada. ¡Hola! Soy Arkaios con Claude. ¿En qué puedo ayudarte?',
        who: 'ai', 
        isSystem: true
      });
    });

    // Probar conexión - COMPLETAMENTE CORREGIDO
    pingBtn.addEventListener('click', async () => {
      pingBtn.disabled = true;
      pingBtn.textContent = 'Probando…';
      setConnecting();
      
      try {
        // Verificar que Puter.js está cargado
        if (typeof puter === 'undefined') {
          throw new Error('Puter.js no está cargado');
        }
        
        if (!puter.ai) {
          throw new Error('puter.ai no está disponible');
        }
        
        // Probar con una consulta muy simple
        console.log('Probando conexión con Claude...');
        const testResponse = await puter.ai.chat("Responde solo: OK", {
          model: "claude-3-5-sonnet",
          stream: false
        });
        
        console.log('Respuesta de prueba:', testResponse);
        
        let responseText;
        if (typeof testResponse === 'string') {
          responseText = testResponse;
        } else if (testResponse?.message?.content) {
          responseText = Array.isArray(testResponse.message.content) ? 
            testResponse.message.content[0]?.text || testResponse.message.content[0] :
            testResponse.message.content;
        } else if (testResponse?.text) {
          responseText = testResponse.text;
        } else {
          responseText = 'Respuesta en formato no estándar';
        }
        
        updateConnectionStatus(true);
        addMessage({
          text: `Conexión exitosa con Puter.js y Claude
Modelo: claude-3-5-sonnet
Respuesta: ${responseText}
Estado: LISTO`,
          who: 'ai', 
          isSystem: true
        });
        
      } catch (error) {
        console.error('Error en ping:', error);
        updateConnectionStatus(false);
        addMessage({
          text: `Error de conexión: ${error.message}

Posibles causas:
- Puter.js no se cargó completamente
- Sin conexión a internet  
- API de Claude temporalmente no disponible
- Modelo seleccionado no soportado

Solución: Recarga la página e inténtalo de nuevo.`,
          who: 'ai', 
          isSystem: true
        });
      } finally {
        pingBtn.disabled = false;
        pingBtn.textContent = 'Probar conexión';
      }
    });

    // Event listeners principales
    sendBtn.addEventListener('click', send);
    
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });

    // Inicialización - COMPLETAMENTE REESCRITA
    async function init() {
      console.log('Inicializando ARKAIOS Claude...');
      
      // Mostrar estado inicial
      addMessage({
        text: 'Iniciando ARKAIOS... Conectando con Puter.js',
        who: 'ai',
        isSystem: true
      });
      
      // Esperar a que Puter.js se cargue
      const puterAvailable = await waitForPuter();
      
      if (puterAvailable) {
        console.log('Puter.js cargado correctamente');
        
        try {
          // Verificar capacidades
          const hasAI = !!(puter?.ai);
          const hasFS = !!(puter?.fs);
          const hasTxt2Img = !!(puter?.ai?.txt2img);
          
          updateConnectionStatus(true);
          addMessage({
            text: `¡Hola! Soy Arkaios con Claude via Puter.js

Sistema listo:
- IA Claude: ${hasAI ? '✓' : '✗'} 
- Sistema archivos: ${hasFS ? '✓' : '✗'}
- Generación imágenes: ${hasTxt2Img ? '✓' : '✗'}

Puedes:
- Adjuntar imágenes y archivos (drag & drop o Ctrl+V)
- Seleccionar diferentes modelos de Claude
- Usar comandos especiales como "img: descripción"

¿En qué puedo ayudarte?`,
            who: 'ai'
          });
          
        } catch (error) {
          console.error('Error verificando capacidades:', error);
          addMessage({
            text: 'Sistema iniciado con limitaciones: ' + error.message,
            who: 'ai',
            isSystem: true
          });
        }
        
      } else {
        console.error('Puter.js no se pudo cargar después de', maxRetries, 'intentos');
        updateConnectionStatus(false);
        addMessage({
          text: `❌ Error: No se pudo conectar con Puter.js después de ${maxRetries} intentos.

Posibles soluciones:
1. Verifica tu conexión a internet
2. Recarga la página (Ctrl+F5)
3. Verifica que https://js.puter.com/v2/ esté accesible
4. Intenta en modo incógnito

Si el problema persiste, Puter.js podría estar experimentando problemas temporales.`,
          who: 'ai',
          isSystem: true
        });
      }
    }

    // Ejecutar inicialización cuando la página cargue
    window.addEventListener('load', init);
  </script>
</body>
</html>