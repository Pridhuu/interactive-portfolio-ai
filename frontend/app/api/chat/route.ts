const BACKEND_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";

export async function POST(req: Request) {
  const body = await req.json();

  const backendRes = await fetch(`${BACKEND_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!backendRes.ok || !backendRes.body) {
    return new Response(
      JSON.stringify({ error: "Backend unavailable." }),
      { status: 502, headers: { "Content-Type": "application/json" } }
    );
  }

  // Pass the SSE stream straight through to the browser
  return new Response(backendRes.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
    },
  });
}
