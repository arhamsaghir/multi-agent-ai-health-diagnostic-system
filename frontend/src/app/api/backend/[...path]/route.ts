import { NextRequest } from "next/server";

/**
 * Same-origin proxy to the AegisMed FastAPI backend.
 *
 * The browser talks to `/api/backend/<backend-path>` and this route handler
 * forwards the call to BACKEND_URL. That keeps the API key server-side
 * (never exposed to the browser), removes CORS from the deployment story,
 * and lets the backend port stay bound to the loopback interface.
 *
 * Streaming responses (SSE agent progress) are forwarded as-is.
 */

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const BACKEND_URL = (process.env.BACKEND_URL ?? "http://localhost:8000").replace(/\/+$/, "");

/**
 * Extra browser origins that may call the portal, beyond the portal's own.
 *
 * Needed when the portal sits behind a reverse proxy that rewrites the
 * Host header — the same-origin check below would otherwise reject the
 * legitimate browser.
 */
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS ?? "")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

type RouteContext = { params: Promise<{ path?: string[] }> };

/**
 * Reject cross-site browser requests.
 *
 * Every request this route forwards carries the service API key, so the
 * proxy is privileged. A page on another origin must not be able to make
 * the victim's browser run a diagnosis through the hospital portal. A
 * request without an Origin header (server-to-server call, curl) is not a
 * browser cross-site request and is allowed.
 */
function originAllowed(request: NextRequest): boolean {
  const origin = request.headers.get("origin");
  if (!origin) return true;
  if (ALLOWED_ORIGINS.includes(origin)) return true;

  const host = request.headers.get("host");
  try {
    return new URL(origin).host === host;
  } catch {
    return false;
  }
}

async function proxy(request: NextRequest, context: RouteContext): Promise<Response> {
  if (!originAllowed(request)) {
    return Response.json(
      { detail: "Cross-origin request refused by the AegisMed backend proxy" },
      { status: 403 },
    );
  }

  const { path = [] } = await context.params;
  const target = new URL(`${BACKEND_URL}/${path.join("/")}`);
  target.search = request.nextUrl.search;

  const headers = new Headers();
  for (const name of ["content-type", "accept"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  const apiKey = process.env.API_KEY ?? request.headers.get("x-api-key");
  if (apiKey) headers.set("x-api-key", apiKey);

  const method = request.method;
  const body =
    method === "GET" || method === "HEAD" ? undefined : await request.arrayBuffer();

  let upstream: Response;
  try {
    upstream = await fetch(target, {
      method,
      headers,
      body: body && body.byteLength > 0 ? body : undefined,
      cache: "no-store",
      redirect: "manual",
    });
  } catch (error) {
    return Response.json(
      { detail: `Backend unreachable at ${BACKEND_URL}: ${(error as Error).message}` },
      { status: 502 },
    );
  }

  const responseHeaders = new Headers();
  for (const name of ["content-type", "content-disposition", "cache-control"]) {
    const value = upstream.headers.get(name);
    if (value) responseHeaders.set(name, value);
  }

  return new Response(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
