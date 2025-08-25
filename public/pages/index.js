// frontend/pages/index.js
import { useState, useEffect, useRef } from 'react';
import Head from 'next/head';

export default function ArkaiosUI() {
  // ==== ESTADOS ====
  const [conversationId, setConversationId] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [pendingFiles, setPendingFiles] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isRootMode, setIsRootMode] = useState(false);
  const [isSending, setIsSending] = useState(false);
  
  const historyRef = useRef(null);
  const fileInputRef = useRef(null);

  // ==== CONSTANTES ====
const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://aeio-mr.onrender.com' 
  : 'http://127.0.0.1:8000';

  // ==== EFECTOS INICIALES ====
  useEffect(() => {
    // Generar ID de conversación
    let cid = localStorage.getItem(CONVO_KEY);
    if (!cid) {
      cid = (crypto.randomUUID && crypto.randomUUID()) || String(Date.now());
      localStorage.setItem(CONVO_KEY, cid);
    }
    setConversationId(cid);
    
    // Mensaje inicial
    addMessage({
      text: '¡Hola! Soy Arkaios (Gemini). Puedes adjuntar imágenes o PDFs para que los tenga en cuenta. Activa «Modo ROOT» si necesitas una acción administrativa.',
      who: 'ai'
    });

    // Verificar conexión inicial
    checkInitialConnection();
  }, []);

  // Scroll al final de los mensajes
  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [messages]);

  // ==== FUNCIONES PRINCIPALES ====
  const addMessage = ({ text, who = 'ai', attachments = [], isSystem = false }) => {
    const newMessage = {
      id: Date.now(),
      text,
      who,
      attachments,
      isSystem,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  };

  const updateConnectionStatus = (connected) => {
    setIsConnected(connected);
  };

  const setConnecting = () => {
    setIsConnected(false);
  };

  // ==== MANEJO DE ARCHIVOS ====
  const handleFileSelect = (e) => {
    const newFiles = Array.from(e.target.files).filter(f => f.size <= 10 * 1024 * 1024);
    if (newFiles.length !== e.target.files.length) {
      addMessage({
        text: 'Algunos archivos fueron omitidos por ser muy grandes (máx 10MB)',
        who: 'ai',
        isSystem: true
      });
    }
    setPendingFiles(prev => [...prev, ...newFiles]);
    e.target.value = '';
  };

  const removePendingFile = (indexToRemove) => {
    setPendingFiles(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  const clearFiles = () => {
    setPendingFiles([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // ==== COMUNICACIÓN CON API ====
  const uploadFiles = async () => {
    if (!pendingFiles.length) return [];
    
    const form = new FormData();
    pendingFiles.forEach(f => form.append('files', f));
    
    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: form
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error al subir archivos: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      const data = await response.json();
      return data.files || [];
    } catch (error) {
      console.error('Error uploading files:', error);
      throw error;
    }
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text && pendingFiles.length === 0) return;
    if (isSending) return;

    // Mostrar mensaje del usuario inmediatamente
    const localPreviews = [];
    for (const file of pendingFiles) {
      if (file.type.startsWith('image/')) {
        try {
          const preview = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
          });
          localPreviews.push({ name: file.name, preview, type: file.type });
        } catch (e) {
          localPreviews.push({ name: file.name, type: file.type });
        }
      } else {
        localPreviews.push({ name: file.name, type: file.type });
      }
    }

    if (text || localPreviews.length) {
      addMessage({
        text: text || '(adjuntos)',
        who: 'user',
        attachments: localPreviews
      });
    }
    
    setInput('');
    setIsSending(true);

    try {
      const uploaded = await uploadFiles();
      const payload = {
        message: text,
        attachments: uploaded,
        root: isRootMode,
        conversationId
      };

      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        let errorMsg;
        try {
          const errorData = await response.json();
          errorMsg = errorData.respuesta || `Error ${response.status}: ${response.statusText}`;
        } catch {
          errorMsg = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      updateConnectionStatus(true);
      addMessage({
        text: data.respuesta || '(sin respuesta)',
        who: 'ai',
        attachments: uploaded
      });

    } catch (err) {
      console.error('Error sending message:', err);
      updateConnectionStatus(false);
      addMessage({
        text: '❌ Error: ' + err.message,
        who: 'ai',
        isSystem: true
      });
    } finally {
      setIsSending(false);
      setPendingFiles([]);
    }
  };

  const clearChat = async () => {
    if (!confirm('¿Estás seguro de que quieres borrar todo el historial y la memoria?')) return;
    
    try {
      await fetch(`${API_BASE}/clear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversationId })
      });
    } catch (e) {
      console.warn('Error clearing memory:', e);
    }
    
    setMessages([]);
    addMessage({
      text: 'Memoria e historial de esta conversación borrados.',
      who: 'ai',
      isSystem: true
    });
    
    // Mensaje inicial después de limpiar
    addMessage({
      text: '¡Hola! Soy Arkaios (Gemini). Puedes adjuntar imágenes o PDFs para que los tenga en cuenta. Activa «Modo ROOT» si necesitas una acción administrativa.',
      who: 'ai'
    });
  };

  const pingServer = async () => {
    setConnecting();
    
    try {
      const response = await fetch(`${API_BASE}/health`, {
        method: 'GET',
        cache: 'no-cache'
      });
      
      if (response.ok) {
        const data = await response.json();
        updateConnectionStatus(true);
        
        const statusMsg = `✅ Servidor OK\n- Estado: ${data.status}\n- Modelo: ${data.model}\n- API configurada: ${data.api_key_configured ? 'Sí' : 'No'}\n- Archivo HTML: ${data.html_file_exists ? 'Encontrado' : 'Faltante'}\n- Directorio: ${data.current_directory}`;
        addMessage({ text: statusMsg, who: 'ai', isSystem: true });
      } else {
        updateConnectionStatus(false);
        addMessage({ text: '❌ Servidor respondió con error: ' + response.status, who: 'ai', isSystem: true });
      }
    } catch (e) {
      updateConnectionStatus(false);
      addMessage({ text: '❌ No se pudo conectar al servidor: ' + e.message, who: 'ai', isSystem: true });
    }
  };

  const checkInitialConnection = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`, {
        method: 'GET',
        cache: 'no-cache'
      });
      updateConnectionStatus(response.ok);
    } catch (e) {
      console.warn('Conexión inicial falló:', e);
      updateConnectionStatus(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // ==== RENDERIZADO ====
  return (
    <>
      <Head>
        <title>Arkaios UI — Gemini</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="https://img.icons8.com/fluency/48/robot-2.png" />
      </Head>

      <div className="wrap">
        <header>
          <h1>ARKAIOS UI</h1>
          <span className="badge">Proveedor: Gemini</span>
          <span className={`status ${isConnected ? 'online' : 'offline'}`}>
            {isConnected ? 'Conectado' : 'Desconectado'}
          </span>
          <span className="right switch" title="Permite órdenes administrativas">
            <input 
              type="checkbox" 
              id="rootToggle"
              checked={isRootMode}
              onChange={(e) => setIsRootMode(e.target.checked)}
            />
            <label htmlFor="rootToggle">Modo ROOT</label>
          </span>
        </header>

        <main id="history" ref={historyRef}>
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`msg ${msg.who} ${msg.isSystem ? 'system' : ''} ${msg.who === 'ai' && isRootMode ? 'root' : ''}`}
            >
              <div className="head">
                {msg.isSystem ? 'Sistema' : msg.who === 'user' ? 'Tú' : (isRootMode ? 'Arkaios (ROOT/Gemini)' : 'Arkaios (Gemini)')}
              </div>
              <div className="content">{msg.text}</div>
              
              {msg.attachments?.length > 0 && (
                <div className="attachments">
                  {msg.attachments.map((attachment, index) => (
                    <div key={index} className="thumb">
                      {attachment.type?.startsWith('image/') ? (
                        <img 
                          src={attachment.preview || attachment.url} 
                          alt={attachment.name}
                          onError={(e) => {
                            e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><text y="50%" x="50%" text-anchor="middle" dy=".3em">❌</text></svg>';
                          }}
                        />
                      ) : (
                        <span>📄 {attachment.name || attachment.url}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </main>

        <section className="panel">
          <div className="filebar">
            <input 
              type="file" 
              ref={fileInputRef}
              multiple 
              accept="image/*,application/pdf,.pdf,.txt,.md,.json" 
              onChange={handleFileSelect}
            />
            <button className="btn" onClick={clearFiles} title="Quitar adjuntos" disabled={pendingFiles.length === 0}>
              Limpiar adjuntos
            </button>
          </div>
          
          {pendingFiles.length > 0 && (
            <div className="previews">
              {pendingFiles.map((file, index) => (
                <div key={index} className="thumb" style={{ position: 'relative' }}>
                  {file.type.startsWith('image/') ? (
                    <img 
                      src={URL.createObjectURL(file)} 
                      alt={file.name}
                      style={{ maxWidth: '100px', maxHeight: '100px' }}
                    />
                  ) : (
                    <span>📄 {file.name}</span>
                  )}
                  <button
                    style={{
                      position: 'absolute',
                      top: '-8px',
                      right: '-8px',
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: 'var(--danger)',
                      color: 'white',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '12px',
                      lineHeight: '1'
                    }}
                    onClick={() => removePendingFile(index)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Escribe tu mensaje…"
            maxLength={4000}
            disabled={isSending}
          />
          
          <div className="row">
            <div>
              <button className="btn" onClick={clearChat} title="Borra historial y memoria">
                Limpiar chat
              </button>
              <button className="btn warning" onClick={pingServer} title="Probar conexión con el backend">
                Ping
              </button>
              <span className="hint">CID: {conversationId ? `${conversationId.slice(0, 8)}…` : 'generando...'}</span>
            </div>
            <button 
              className={`btn primary ${isSending ? 'loading' : ''}`}
              onClick={sendMessage}
              disabled={isSending || (!input.trim() && pendingFiles.length === 0)}
            >
              {isSending ? 'Enviando...' : 'Enviar'}
            </button>
          </div>
        </section>
      </div>

      <style jsx>{`
        :root {
          --bg: #091017;
          --surface: #0d1a28;
          --ink: #e6f1ff;
          --muted: #9fb4d3;
          --brand: #00e1a3;
          --accent: #4ea2ff;
          --danger: #ff5b8a;
          --line: #14314f;
        }
        
        * {
          box-sizing: border-box;
        }
        
        html, body {
          height: 100%;
          margin: 0;
          font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
          background: var(--bg);
          color: var(--ink);
        }
        
        .wrap {
          max-width: 1100px;
          margin: 0 auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
          height: 100vh;
        }
        
        header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
          flex-wrap: wrap;
        }
        
        header h1 {
          font-size: 20px;
          margin: 0;
        }
        
        .badge {
          font-size: 12px;
          padding: 4px 8px;
          border-radius: 999px;
          background: #0e253e;
          border: 1px solid var(--line);
          color: #bfe2ff;
        }
        
        .status {
          font-size: 11px;
          padding: 2px 6px;
          border-radius: 12px;
          margin-left: 8px;
        }
        
        .status.online {
          background: #004225;
          color: #00e1a3;
          border: 1px solid #006b3d;
        }
        
        .status.offline {
          background: #3d1a1a;
          color: #ff5b8a;
          border: 1px solid #5c2929;
        }
        
        .status.connecting {
          background: #3d3d1a;
          color: #e1e100;
          border: 1px solid #5c5c29;
        }
        
        #history {
          flex: 1;
          overflow: auto;
          border: 1px solid var(--line);
          border-radius: 12px;
          padding: 14px;
          background: rgba(255, 255, 255, 0.03);
          margin-bottom: 12px;
        }
        
        .msg {
          padding: 12px;
          border-radius: 12px;
          margin-bottom: 12px;
          opacity: 0;
          animation: fadeIn 0.3s forwards;
        }
        
        .msg.user {
          background: rgba(0, 225, 163, 0.14);
          border: 1px solid rgba(0, 225, 163, 0.35);
          margin-left: 15%;
        }
        
        .msg.ai {
          background: rgba(78, 162, 255, 0.12);
          border: 1px solid rgba(78, 162, 255, 0.35);
          margin-right: 15%;
        }
        
        .msg.root {
          background: rgba(255, 91, 138, 0.12);
          border: 1px solid rgba(255, 91, 138, 0.35);
        }
        
        .msg.system {
          background: rgba(255, 193, 7, 0.1);
          border: 1px solid rgba(255, 193, 7, 0.3);
          text-align: center;
        }
        
        .head {
          font-size: 12px;
          color: var(--muted);
          margin-bottom: 6px;
        }
        
        .content {
          white-space: pre-wrap;
          line-height: 1.6;
        }
        
        .attachments {
          margin-top: 8px;
          border-top: 1px dashed var(--line);
          padding-top: 8px;
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        
        .thumb {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          border: 1px solid var(--line);
          padding: 6px;
          border-radius: 8px;
          background: var(--surface);
        }
        
        .thumb img {
          max-width: 160px;
          max-height: 110px;
          border-radius: 6px;
          display: block;
        }
        
        .panel {
          border: 1px solid var(--line);
          background: var(--surface);
          border-radius: 12px;
          padding: 12px;
        }
        
        textarea {
          width: 100%;
          min-height: 90px;
          resize: none;
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid var(--line);
          border-radius: 10px;
          padding: 12px;
          color: var(--ink);
          font-family: inherit;
        }
        
        textarea:focus {
          outline: none;
          border-color: var(--brand);
        }
        
        .row {
          display: flex;
          gap: 8px;
          align-items: center;
          justify-content: space-between;
          margin-top: 8px;
          flex-wrap: wrap;
        }
        
        .btn {
          cursor: pointer;
          border-radius: 10px;
          padding: 10px 14px;
          border: 1px solid var(--line);
          background: transparent;
          color: var(--ink);
          font-size: 13px;
          transition: all 0.2s;
          font-family: inherit;
        }
        
        .btn:hover {
          border-color: var(--brand);
          background: rgba(0, 225, 163, 0.1);
        }
        
        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .btn.primary {
          background: var(--brand);
          color: #001b12;
          border: none;
          font-weight: 600;
        }
        
        .btn.primary:hover {
          background: #00c491;
        }
        
        .btn.primary:disabled {
          background: #006b51;
          color: #4a9d7a;
        }
        
        .btn.warning {
          border-color: #ff9db8;
          color: #ffd0dd;
        }
        
        .btn.warning:hover {
          background: rgba(255, 91, 138, 0.1);
        }
        
        .filebar {
          display: flex;
          gap: 10px;
          align-items: center;
          margin-top: 8px;
          flex-wrap: wrap;
        }
        
        .previews {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          margin-top: 8px;
        }
        
        .right {
          margin-left: auto;
        }
        
        .switch {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: #15283f;
          border: 1px solid var(--line);
          padding: 6px 10px;
          borderRadius: 999px;
        }
        
        .switch input {
          accent-color: var(--danger);
        }
        
        .hint {
          font-size: 12px;
          color: var(--muted);
        }
        
        .loading {
          opacity: 0.6;
        }
        
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        /* Responsivo */
        @media (max-width: 768px) {
          .wrap {
            padding: 8px;
          }
          
          .msg.user {
            margin-left: 5%;
          }
          
          .msg.ai {
            margin-right: 5%;
          }
          
          .filebar {
            flex-direction: column;
            align-items: stretch;
          }
          
          .row {
            flex-direction: column;
            align-items: stretch;
          }
          
          .right {
            margin-left: 0;
          }
        }
      `}</style>
    </>
  );
}