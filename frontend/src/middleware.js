import { NextResponse } from 'next/server';
import { decodeJwt } from 'jose';

export async function middleware(request) {
  const sessionCookie = request.cookies.get('_at');
  const refreshCookie = request.cookies.get('_rt');
  const { pathname } = request.nextUrl;

  // Define public routes that don't require authentication
  const publicRoutes = ['/auth/sign-in', '/auth/sign-up'];
  const isPublicRoute = publicRoutes.some(route =>
    pathname === route || pathname.startsWith(`${route}/`)
  );

  // Handle public routes
  if (isPublicRoute) {
    if (sessionCookie) {
      return NextResponse.redirect(new URL('/', request.url));
    }
    return NextResponse.next();
  }

  let isTokenValid = false;
  if (sessionCookie) {
    try {
      const decoded = decodeJwt(sessionCookie.value);
      const currentTime = Math.floor(Date.now() / 1000);
      if (decoded.exp && decoded.exp > currentTime) {
        isTokenValid = true;
      }
    } catch (error) {
      console.error('Error decoding access token:', error);
    }
  }

  // If access token is invalid or missing, attempt to refresh
  if (!isTokenValid) {
    if (refreshCookie) {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}auth/refresh`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'Cookie': `_rt=${refreshCookie.value}`,
          },
        });

        if (response.ok) {
          const nextResponse = NextResponse.next();
          const setCookieHeaders = response.headers.getSetCookie();
          setCookieHeaders.forEach(cookie => {
            nextResponse.headers.append('Set-Cookie', cookie);
          });
          return nextResponse;
        } else {
          return NextResponse.redirect(new URL('/auth/sign-in', request.url));
        }
      } catch (error) {
        console.error('Error refreshing token:', error);
        return NextResponse.redirect(new URL('/auth/sign-in', request.url));
      }
    } else {
      // No refresh token available, redirect to sign-in
      return NextResponse.redirect(new URL('/auth/sign-in', request.url));
    }
  }

  // Access token is valid, proceed with the request
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|images|favicon.ico).*)'],
};