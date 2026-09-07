import Chat from "./components/Chat";

export default function App() {
  return (
    <div className="app">
      <header className="app__header">
        <h1>Agentic Medical Operations Assistant</h1>
        <p className="app__disclaimer">
          Educational demo. Not a medical diagnosis and not a substitute for a
          healthcare professional. All data is synthetic.
        </p>
      </header>
      <main className="app__main">
        <Chat />
      </main>
    </div>
  );
}
