// scripts/vercel-check.js
const fs = require('fs');
const path = require('path');

// Verificar archivos esenciales
const requiredFiles = [
  'package.json',
  'next.config.js',
  'public/',
  'pages/'
];

requiredFiles.forEach(file => {
  if (!fs.existsSync(path.join(__dirname, '..', file))) {
    console.error(`❌ Falta: ${file}`);
    process.exit(1);
  }
});

console.log('✅ Todos los archivos necesarios están presentes');