// middleware.js (en la raíz)
import { NextResponse } from 'next/server'

export function middleware(request) {
  // Verificar si es una solicitud del servidor
  const response = NextResponse.next()
  
  // Opcional: restringir acceso solo desde ciertos dominios
  const allowedOrigins = ['https://aeio-mr.vercel.app']
  const origin = request.headers.get('origin')
  
  if (origin && !allowedOrigins.includes(origin)) {
    return new NextResponse(null, { status: 403 })
  }
  
  return response
}

export const config = {
  matcher: '/:path*'
}