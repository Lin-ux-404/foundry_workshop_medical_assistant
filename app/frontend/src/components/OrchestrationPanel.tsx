import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { ArrowDown, ArrowRight, Check, ChevronDown, Clock3, List, ListChecks, Network, X } from "lucide-react";
import type { AgentId, AgentIdentity, Run } from "../api";

import LedgerView from "./LedgerView";

import { agents } from "../agents";
import Markdown from "./Markdown";
const ids = Object.keys(agents) as AgentId[];

export default function OrchestrationPanel({ runs, selectedId, onSelect, onClose, identities }: {
  runs: Run[]; selectedId: string | null; onSelect: (id: string) => void; onClose: () => void; identities: AgentIdentity[];
}) {
  const run = runs.find(item => item.id === selectedId) || runs[runs.length - 1];
  const [selected, setSelected] = useState<AgentId | null>(null);
  const [tab, setTab] = useState<"graph" | "timeline" | "ledger">("graph");
  const [graphGeometry, setGraphGeometry] = useState<{ width: number; height: number; edges: { d: string; x: number; y: number }[] }>({ width: 1, height: 1, edges: [] });
  const graphRef = useRef<HTMLDivElement>(null);
  const nodeRefs = useRef<Partial<Record<AgentId, HTMLButtonElement>>>({});
  const closeRef = useRef<HTMLButtonElement>(null);
  useEffect(() => { setSelected(null); }, [run?.id]);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    function escape(event: KeyboardEvent) { if (event.key === "Escape") onClose(); }
    document.addEventListener("keydown", escape);
    return () => { document.removeEventListener("keydown", escape); previous?.focus(); };
  }, [onClose]);
  const calls = run?.calls || [];
  const visibleCalls = selected ? calls.filter(call => call.agent === selected) : calls;
  const count = (agent: AgentId) => calls.filter(call => call.agent === agent).length;
  const running = (agent: AgentId) => calls.some(call => call.agent === agent && call.status === "running");

  // Derive each connection from the rendered card bounds. Fixed SVG coordinates
  // drift when the panel is resized or the cards wrap at different breakpoints.
  useLayoutEffect(() => {
    const canvas = graphRef.current;
    if (!canvas || tab !== "graph") return;
    const measure = () => {
      const canvasRect = canvas.getBoundingClientRect();
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      const manager = nodeRefs.current.manager;
      if (!manager || width === 0 || height === 0) return;
      const relativeRect = (node: HTMLButtonElement) => {
        const rect = node.getBoundingClientRect();
        return { x: rect.left - canvasRect.left, y: rect.top - canvasRect.top, width: rect.width, height: rect.height };
      };
      const source = relativeRect(manager);
      const center = (rect: { x: number; y: number; width: number; height: number }) => ({ x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 });
      const edgePoint = (rect: { x: number; y: number; width: number; height: number }, toward: { x: number; y: number }) => {
        const origin = center(rect);
        const dx = toward.x - origin.x;
        const dy = toward.y - origin.y;
        const scale = Math.min((rect.width / 2) / Math.max(Math.abs(dx), 0.001), (rect.height / 2) / Math.max(Math.abs(dy), 0.001));
        return { x: origin.x + dx * scale, y: origin.y + dy * scale };
      };
      const edges = (["researcher", "communicator", "knowledge_specialist", "safety_reviewer"] as AgentId[]).map(id => {
        const targetNode = nodeRefs.current[id];
        if (!targetNode) return { d: "", x: 0, y: 0 };
        const target = relativeRect(targetNode);
        const sourceCenter = center(source);
        const targetCenter = center(target);
        const start = edgePoint(source, targetCenter);
        const end = edgePoint(target, sourceCenter);
        const dx = end.x - start.x;
        const dy = end.y - start.y;
        const c1 = { x: start.x + dx * 0.32, y: start.y + dy * 0.24 };
        const c2 = { x: start.x + dx * 0.68, y: start.y + dy * 0.76 };
        const t = 0.5;
        const mt = 1 - t;
        const x = mt ** 3 * start.x + 3 * mt ** 2 * t * c1.x + 3 * mt * t ** 2 * c2.x + t ** 3 * end.x;
        const y = mt ** 3 * start.y + 3 * mt ** 2 * t * c1.y + 3 * mt * t ** 2 * c2.y + t ** 3 * end.y;
        return { d: `M ${start.x} ${start.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${end.x} ${end.y}`, x, y };
      });
      setGraphGeometry({ width, height, edges });
    };
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(canvas);
    Object.values(nodeRefs.current).forEach(node => node && observer.observe(node));
    window.addEventListener("resize", measure);
    return () => { observer.disconnect(); window.removeEventListener("resize", measure); };
  }, [tab, run?.id, identities]);

  return <aside className="trace-panel" aria-label="Conversation history">
    <header className="panel-header"><div><span className="eyebrow">BEHIND THE CONVERSATION</span><h2>Team activity <span className="count-badge">{runs.length}</span></h2></div><button ref={closeRef} className="icon-button" onClick={onClose} aria-label="Close conversation history"><X size={19} /></button></header>
    <div className="panel-content">
      <div className="run-selector"><label htmlFor="run-select">CONVERSATION RUN</label><div><select id="run-select" value={run?.id || ""} onChange={e => onSelect(e.target.value)} disabled={!runs.length}>{!runs.length && <option value="">No conversations yet</option>}{runs.map((item, index) => <option key={item.id} value={item.id}>{`Run ${index + 1}`} · {item.prompt}</option>)}</select><ChevronDown size={15} /></div></div>
      <div className="run-status"><span className={`status-dot ${run?.status || "idle"}`} />{run ? (run.status === "running" ? "Your team is collaborating" : `Run ${run.status}`) : "Ready for your first question"}<span className="magentic-label">Magentic</span></div>
      <div className="metrics"><div><strong>{ids.filter(id => count(id) > 0).length}<small> / {ids.length}</small></strong><span>Agents involved</span></div><div><strong>{calls.length}</strong><span>Agent calls</span></div><div><strong>{run?.durationMs ? `${(run.durationMs / 1000).toFixed(1)}` : "—"}<small>{run?.durationMs ? " s" : ""}</small></strong><span>Total duration</span></div></div>
            <details className="foundry-identities"><summary>Agent names in Foundry</summary><p>The app connects to these Foundry names. Registered versions appear after the first successful connection.</p>{(run?.agents?.length ? run.agents : identities).map(identity => <div key={identity.id}><strong>{agents[identity.id].name}</strong><code>{identity.name}</code><span>{identity.registered ? `Registered · version ${identity.version}` : "Registration pending"}</span></div>)}</details>
      {run?.status === "running" && <div className="current-work"><span className="status-dot running" /><div><strong>In progress</strong><p>{run.tasks.find(task => task.status === "running")?.instruction || (run.calls.some(call => call.agent === "manager" && call.status === "running") ? "Coordinator is updating the plan and progress ledger." : "Connecting to the agent team…")}</p></div></div>}
      <div className="panel-tabs" role="tablist" aria-label="Activity view"><button id="graph-tab" role="tab" aria-controls="activity-view" aria-selected={tab === "graph"} onClick={() => setTab("graph")}><Network size={15} />Graph view</button><button id="timeline-tab" role="tab" aria-controls="activity-view" aria-selected={tab === "timeline"} onClick={() => setTab("timeline")}><List size={15} />Timeline</button><button id="ledger-tab" role="tab" aria-controls="activity-view" aria-selected={tab === "ledger"} onClick={() => setTab("ledger")}><ListChecks size={15} />Ledger & tasks</button></div>
      <div id="activity-view" role="tabpanel" aria-labelledby={`${tab}-tab`}>
      {tab === "graph" && <>
        <div className="graph-canvas" ref={graphRef}>
          <div className="graph-caption"><span className="status-dot completed" /> {run?.status === "running" ? "Live activity" : "Orchestration map"}</div>
          <svg className="graph-lines" viewBox={`0 0 ${graphGeometry.width} ${graphGeometry.height}`} preserveAspectRatio="none" aria-label="Agent communication connections">
            <defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto-start-reverse"><path d="M0 0 L6 3 L0 6" fill="none" stroke="currentColor" strokeWidth="1.2" /></marker></defs>
            {(["researcher", "communicator", "knowledge_specialist", "safety_reviewer"] as AgentId[]).map((id, index) => {
              const edge = graphGeometry.edges[index];
              if (!edge?.d) return null;
              return <g key={id} className={`graph-edge ${selected === id ? "selected" : ""} ${running(id) ? "active" : ""}`} role="button" tabIndex={0} aria-label={`View coordinator and ${agents[id].name} messages, ${count(id)} calls`} onClick={() => setSelected(id)} onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setSelected(id); } }}>
                <path d={edge.d} className="edge-hit" /><path d={edge.d} className="graph-path" markerStart="url(#arrow)" markerEnd="url(#arrow)" />
                <rect x={edge.x - 16} y={edge.y - 10} width="32" height="20" rx="7" /><text x={edge.x} y={edge.y + 4} textAnchor="middle">{count(id)}</text>
              </g>;
            })}
          </svg>
          {ids.map(id => { const agent = agents[id]; const Icon = agent.icon; return <button key={id} ref={node => { if (node) nodeRefs.current[id] = node; else delete nodeRefs.current[id]; }} className={`agent-node agent-node--${id} ${selected === id ? "selected" : ""}`} onClick={() => setSelected(id)} aria-label={`${agent.name}, ${count(id)} calls. View messages`} aria-pressed={selected === id}><span className={`agent-icon ${agent.color}`}><Icon size={17} /></span><span><strong>{agent.name}</strong><small>{agent.role}</small></span><span className={`node-count ${running(id) ? "pulse" : ""}`}>{count(id)}<small>calls</small></span></button>; })}
        </div>
        <p className="graph-hint">Select an agent or a connection to explore its messages.</p>
      </>}
      {tab === "ledger" ? <LedgerView run={run} /> : <><div className="exchange-header"><h3>{selected ? agents[selected].name : "All activity"}<span>{visibleCalls.length}</span></h3>{selected && <button onClick={() => setSelected(null)}>Show all <X size={12} /></button>}</div>
      {!visibleCalls.length ? <div className="activity-empty"><Network size={25} /><strong>{run ? "No calls for this agent yet" : "No activity yet"}</strong><p>{run ? "Calls and messages appear here as the team works." : "Send a message to see the actual agent calls, shared messages, and progress."}</p></div> : <div className="call-list">{visibleCalls.map(call => {
        const agent = agents[call.agent]; const Icon = agent.icon;
        return <details className="call-card" key={call.id} open={visibleCalls.length === 1 ? true : undefined}>
          <summary><span className={`agent-icon ${agent.color}`}><Icon size={15} /></span><div><strong>{call.agent === "manager" ? "Coordinator" : "Coordinator ↔ " + agent.name}</strong><span>Call {calls.indexOf(call) + 1} · {call.messages.length} input messages</span></div><span className="call-time">{call.status === "running" ? <span className="status-dot running" /> : call.status === "failed" ? "Failed" : <Check size={12} />}{call.duration_ms !== null ? `${(call.duration_ms / 1000).toFixed(1)}s` : "Live"}</span><ChevronDown size={14} /></summary>
          <div className="call-detail"><div className="detail-label"><ArrowDown size={12} />INPUT CONTEXT</div>{call.messages.map((message, index) => <div className="trace-message" key={index}><span>{message.author || message.role}</span><Markdown content={message.content || "(No text content)"} /></div>)}<div className="detail-label"><ArrowRight size={12} />{agent.name.toUpperCase()} RESPONSE</div><Markdown className="response-text" content={call.response || (call.status === "failed" ? "The call failed before a response was received." : "Waiting for the agent…")} /><div className="trace-time"><Clock3 size={11} />{new Date(call.started_at).toLocaleTimeString()}</div></div>
        </details>;
      })}</div>}</>}
      </div>
    </div>
    <footer className="panel-footer"><span className="status-dot" />Actual agent inputs & outputs · this session only</footer>
  </aside>;
}




