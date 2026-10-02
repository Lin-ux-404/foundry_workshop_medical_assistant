import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import { ArrowRight, GitBranch, Send, Sparkles, Square, X } from "lucide-react";
import { getHealth, sendChat, type AgentIdentity, type ChatMessage, type Run } from "../api";

import OrchestrationPanel from "./OrchestrationPanel";
import { agents } from "../agents";
import Markdown from "./Markdown";

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [panelOpen, setPanelOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const controller = useRef<AbortController | null>(null);
  const closePanel = useCallback(() => setPanelOpen(false), []);
  const [identities, setIdentities] = useState<AgentIdentity[]>([]);

  useEffect(() => {
    const abort = new AbortController();
    getHealth(abort.signal).then(data => { setIdentities(data.agents || []); }).catch(() => undefined);
    return () => { abort.abort(); controller.current?.abort(); };
  }, []);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [messages, loading]);

  function clearChat() {
    controller.current?.abort(); controller.current = null;
    setLoading(false); setMessages([]); setRuns([]); setSelectedId(null); setError(null); setInput("");
    inputRef.current?.focus();
  }
  async function handleSend(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || loading) return;
    const abort = new AbortController(); controller.current = abort;
    const id = crypto.randomUUID(); const startedAt = Date.now();
    const history = messages;
    setMessages([...history, { role: "user", content: text }]);
    setRuns(previous => [...previous, { id, prompt: text, status: "running", calls: [], tasks: [], ledger: [], agents: identities, startedAt }]);
    setSelectedId(id); setError(null); setInput(""); setLoading(true);
    setPanelOpen(true);
    try {
      await sendChat(text, history, event => {
        if (abort.signal.aborted) return;
        if (event.type === "call") {
          setRuns(previous => previous.map(run => run.id !== id ? run : { ...run, calls: run.calls.some(call => call.id === event.call.id) ? run.calls.map(call => call.id === event.call.id ? event.call : call) : [...run.calls, event.call] }));
        } else if (event.type === "agent_delta") {
          setRuns(previous => previous.map(run => run.id !== id ? run : { ...run, calls: run.calls.map(call => call.id === event.call_id ? { ...call, response: call.response + event.text } : call) }));
        } else if (event.type === "task") {
          setRuns(previous => previous.map(run => run.id !== id ? run : { ...run, tasks: run.tasks.some(task => task.id === event.task.id) ? run.tasks.map(task => task.id === event.task.id ? event.task : task) : [...run.tasks, event.task] }));
        } else if (event.type === "ledger") {
          setRuns(previous => previous.map(run => run.id !== id ? run : { ...run, ledger: [...run.ledger, event.entry] }));
        } else if (event.type === "agents") {
          setIdentities(event.agents);
          setRuns(previous => previous.map(run => run.id !== id ? run : { ...run, agents: event.agents }));
        } else if (event.type === "reply") {
          setMessages(previous => [...previous, { role: "assistant", content: event.reply, runId: id }]);
          setRuns(previous => previous.map(run => run.id === id ? { ...run, status: "completed", durationMs: Date.now() - startedAt } : run));
        }
      }, abort.signal);
    } catch (err) {
      if (controller.current !== abort) return;
      const cancelled = abort.signal.aborted;
      setRuns(previous => previous.map(run => run.id === id ? { ...run, status: cancelled ? "cancelled" : "failed", durationMs: Date.now() - startedAt, tasks: run.tasks.map(task => task.status === "running" || task.status === "pending" ? { ...task, status: cancelled ? "cancelled" : "failed" } : task), calls: run.calls.map(call => call.status === "running" ? { ...call, status: "failed" } : call) } : run));
      if (!cancelled) { setError(err instanceof Error ? err.message : "Something went wrong."); setInput(text); }
    } finally {
      if (controller.current === abort) { setLoading(false); controller.current = null; inputRef.current?.focus(); }
    }
  }
  const activeCall = runs[runs.length - 1]?.calls.slice().reverse().find(call => call.status === "running");

  return <div className={`app ${panelOpen ? "app--expanded" : ""}`}>
    <header className="app__header"><span className="app__eyebrow">Agentic care support</span><h1>Medical Assistant</h1></header>
    <main className="app__main">
      <div className="chat">
        <div className="chat__header">
          <div className="chat__identity"><span className="chat__icon" aria-hidden="true"><Sparkles size={19} strokeWidth={2} /></span><div><h2>AI health assistant</h2></div></div>
          <div className="chat__actions"><button className={`history-button ${panelOpen ? "selected" : ""}`} aria-expanded={panelOpen} onClick={() => setPanelOpen(!panelOpen)}><GitBranch size={16} /><span>View conversation history</span>{runs.length > 0 && <span className="count-badge">{runs.length}</span>}</button><button className="chat__clear" onClick={clearChat} disabled={!messages.length && !error && !loading} aria-label="Clear conversation" title="Clear conversation"><X size={18} /></button></div>
        </div>
        <div className="chat__messages" aria-live="polite">
          {!messages.length ? <div className="chat__empty"><h3>How can I help you today?</h3><p>Describe how you are feeling or ask a general health question to get started.</p></div> : <>

            {messages.map((message, index) => <div key={index} className={`message message--${message.role}`}><span className="message__label">{message.role === "user" ? "You" : "Assistant"}</span><div className={`bubble bubble--${message.role}`}><Markdown content={message.content} /></div>{message.runId && <button className="response-trace" onClick={() => { setSelectedId(message.runId!); setPanelOpen(true); }}><GitBranch size={12} />{runs.find(run => run.id === message.runId)?.calls.length || 0} agent calls<span>View conversation</span><ArrowRight size={12} /></button>}</div>)}
            {loading && <div className="message message--assistant"><span className="message__label">{activeCall ? `${agents[activeCall.agent].name} is working…` : "Your team is getting started…"}</span><div className="bubble bubble--assistant bubble--typing"><span /><span /><span /><span className="sr-only">Thinking</span></div><button className="response-trace" onClick={() => setPanelOpen(true)}>View team activity<ArrowRight size={12} /></button></div>}
          </>}
          <div ref={endRef} />
        </div>
        <div className="chat__composer">
          {error && <div className="chat__error" role="alert">{error}</div>}
          <form className="chat__form" onSubmit={handleSend}><textarea ref={inputRef} className="chat__input" value={input} onChange={e => setInput(e.target.value)} placeholder="Type your message..." disabled={loading} aria-label="Message" rows={1} maxLength={8000} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); e.currentTarget.form?.requestSubmit(); } }} />{loading ? <button className="chat__send" type="button" aria-label="Stop response" onClick={() => controller.current?.abort()}><Square size={15} fill="currentColor" /></button> : <button className="chat__send" type="submit" disabled={!input.trim()} aria-label="Send message"><Send size={19} /></button>}</form>
        </div>
      </div>
      {panelOpen && <OrchestrationPanel runs={runs} selectedId={selectedId} onSelect={setSelectedId} onClose={closePanel} identities={identities} />}
    </main>
    <footer className="app__footer">This demo does not provide a diagnosis or replace a healthcare professional. All data is synthetic.</footer>
  </div>;
}


