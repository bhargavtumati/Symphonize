import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const session = request.cookies.get('firebaseIdToken');
  const searchParams = new URL(request.url).searchParams;
  const code = searchParams.get('code');

  // Allow Zoom integration flow even if no token in cookies
  if (code && request.nextUrl.pathname === '/integrations/zoom-integrations') {
    return NextResponse.next();
  }

  if (!session && request.nextUrl.pathname !== '/') {
    return NextResponse.redirect(new URL('/', request.url));
  }

  if (session && request.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}


export const config = {
  matcher: ['/dashboard/:path*', '/',"/integrations/:path*", "/applicants/:path*", "/organization/:path*" ],
};