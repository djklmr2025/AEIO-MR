import { useState, useEffect } from 'react';
import Head from 'next/head';

export default function Home() {
  const [message, setMessage] = useState('Cargando...');

  useEffect(() => {
    setMessage('¡Hola! AEIO-MR está funcionando con Next.js');
  }, []);

  return (
    <>
      <Head>
        <title>AEIO-MR - Next.js</title>
        <meta name="description" content="Proyecto AEIO-MR con Next.js" />
      </Head>
      
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center', 
        fontFamily: 'system-ui, sans-serif',
        background: '#091017',
        color: '#e6f1ff',
        minHeight: '100vh'
      }}>
        <h1>AEIO-MR</h1>
        <p>{message}</p>
        <p>🚀 Frontend funcionando desde carpeta /frontend</p>
        <p>📁 Estructura correcta para Vercel</p>
      </div>
    </>
  );
}
