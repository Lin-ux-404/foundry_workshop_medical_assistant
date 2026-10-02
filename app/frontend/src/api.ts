const BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export type AgentId = "manager" | "researcher" | "communicator" | "knowledge_specialist" | "safety_reviewer";
export interface AgentIdentity { id: AgentId; name: string; version: string | null; registered: boolean }
export interface Task {
  id: string; agent: AgentId; instruction: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  created_at: string; call_id: string | null;
}
export interface LedgerItem { answer: boolean | string; reason: string }
export interface LedgerEntry {
  id: string; kind: "plan_created" | "replanned" | "progress"; timestamp: string; text: string;
  progress: Record<"is_request_satisfied" | "is_in_loop" | "is_progress_being_made" | "next_speaker" | "instruction_or_question", LedgerItem> | null;
}
export interface ChatMessage { role: "user" | "assistant"; content: string; runId?: string }
export interface TraceMessage { role: string; author: string | null; content: string }
export interface AgentCall {
  id: string;
  agent: AgentId;
  status: "running" | "completed" | "failed";
  started_at: string;
  duration_ms: number | null;
  messages: TraceMessage[];
  response: string;
}
export interface Run {
  id: string;
  prompt: string;
  status: "running" | "completed" | "failed" | "cancelled";
  calls: AgentCall[];
  tasks: Task[];
  ledger: LedgerEntry[];
  agents: AgentIdentity[];
  startedAt: number;
  durationMs?: number;
}
export type StreamEvent =
  | { type: "call"; call: AgentCall }
  | { type: "agent_delta"; call_id: string; agent: AgentId; text: string }
  | { type: "ledger"; entry: LedgerEntry }
  | { type: "task"; task: Task }
  | { type: "agents"; agents: AgentIdentity[] }
  | { type: "reply"; reply: string }
  | { type: "error"; message: string };

export async function getHealth(signal?: AbortSignal): Promise<{ configured: boolean; agents: AgentIdentity[] }> {
  const response = await fetch(`${BASE}/api/health`, { signal });
  if (!response.ok) throw new Error("Backend unavailable");
  return response.json();
}

export async function sendChat(message: string, history: ChatMessage[], onEvent: (event: StreamEvent) => void, signal: AbortSignal) {
  const res = await fetch(`${BASE}/api/chat/stream`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history: history.map(({ role, content }) => ({ role, content })) }), signal,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new Error(typeof data?.detail === "string" ? data.detail : `Request failed (${res.status})`);
  }
  if (!res.body) throw new Error("The server returned an empty stream.");
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let terminal = false;
  function receive(line: string) {
    if (!line.trim()) return;
    const event = JSON.parse(line) as StreamEvent;
    if (event.type === "error") throw new Error(event.message);
    if (event.type === "reply") terminal = true;
    onEvent(event);
  }
  try {
    while (true) {
      const { done, value } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      lines.forEach(receive);
      if (done) break;
    }
    receive(buffer);
    if (!terminal) throw new Error("The connection ended before the team finished. Please try again.");
  } finally {
    await reader.cancel().catch(() => undefined);
    reader.releaseLock();
  }
}
