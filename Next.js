# Crea el archivo principal de Next.js
cat > pages/index.js << 'EOF'
import Head from 'next/head'

export default function Home() {
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
        <p>🚀 Funcionando con Next.js</p>
        <p>✅ Listo para deploy en Vercel</p>
      </div>
    </>
  )
}
EOF