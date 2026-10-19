export async function onRequestPost() {
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'Set-Cookie': 'sess=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0',
    },
  });
}
