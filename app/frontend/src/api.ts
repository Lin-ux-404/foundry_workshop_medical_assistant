// Thin API client for the backend. When using the Vite dev proxy, BASE is "".
const BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export interface ChatResponse {
  reply: string;
}

export async function sendChat(message: string): Promise<string> {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) {
    throw new Error(`Request failed (${res.status})`);
  }
  const data: ChatResponse = await res.json();
  return data.reply;
}
