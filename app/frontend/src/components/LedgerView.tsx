import { Check, Circle, Clock3, LoaderCircle, ListChecks } from "lucide-react";
import type { Run } from "../api";
import { agents } from "../agents";
import Markdown from "./Markdown";

const progressLabels: Record<string, string> = {
  is_request_satisfied: "Request satisfied", is_in_loop: "Loop detected",
  is_progress_being_made: "Making progress", next_speaker: "Next agent",
  instruction_or_question: "Next assignment",
};

export default function LedgerView({ run }: { run?: Run }) {
  const entries = run?.ledger || [];
  const tasks = run?.tasks || [];
  const latest = entries.filter(entry => entry.progress).slice(-1)[0]?.progress;
  return <div className="ledger-view">
    <div className="exchange-header"><h3>Assigned tasks <span>{tasks.length}</span></h3><span className="task-total">{tasks.filter(task => task.status === "completed").length} completed</span></div>
    {!tasks.length ? <p className="ledger-empty">{run?.status === "running" ? "The coordinator is preparing the plan. Assigned tasks will appear here." : "Tasks appear when the coordinator assigns work during a live conversation."}</p> : <ol className="task-list">{tasks.map(task => <li key={task.id}>
      <span className={`task-indicator task-indicator--${task.status}`}>{task.status === "completed" ? <Check size={15} /> : task.status === "running" ? <LoaderCircle size={15} className="spin" /> : <Circle size={13} />}</span>
      <div><div className="task-heading"><strong>{agents[task.agent].name}</strong><span>{task.status.replace("pending", "queued")}</span></div><Markdown content={task.instruction} />{task.call_id && <small>Call {run!.calls.findIndex(call => call.id === task.call_id) + 1}</small>}</div>
    </li>)}</ol>}
    {latest && <section className="progress-ledger"><h3>Latest progress ledger</h3>{Object.entries(latest).map(([key, item]) => <div className="ledger-field" key={key}><div><strong>{progressLabels[key]}</strong><span>{typeof item.answer === "boolean" ? item.answer ? "Yes" : "No" : item.answer}</span></div>{item.reason && <Markdown content={item.reason} />}</div>)}</section>}
    <div className="exchange-header"><h3><ListChecks size={16} />Ledger history <span>{entries.length}</span></h3></div>
    {!entries.length && <p className="ledger-empty">The actual task plan, facts, replans, and progress decisions will be recorded here. No ledger has been generated yet.</p>}
    <div className="ledger-entries">{entries.map((entry, index) => <details className="ledger-entry" key={entry.id} open={entry.kind !== "progress" ? true : undefined}><summary>{index + 1}. {entry.kind === "plan_created" ? "Task ledger · initial plan" : entry.kind === "replanned" ? "Task ledger · revised plan" : "Progress ledger"}<span><Clock3 size={11} />{new Date(entry.timestamp).toLocaleTimeString()}</span></summary><div>{entry.text ? <Markdown content={entry.text} /> : Object.entries(entry.progress || {}).map(([key, item]) => <div className="ledger-field" key={key}><strong>{progressLabels[key]}: {String(item.answer)}</strong><Markdown content={item.reason} /></div>)}</div></details>)}</div>
  </div>;
}


