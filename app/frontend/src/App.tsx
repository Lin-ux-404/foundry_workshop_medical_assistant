import Chat from "./components/Chat";

export default function App() {
  return (
    <div className="app">
      <header className="app__header">
        <span className="app__eyebrow">Agentic care support</span>
        <h1>Medical Assistant</h1>
        <p className="app__disclaimer">
          Ask a health question and get clear, educational guidance from our AI
          assistant.
        </p>
      </header>
      <main className="app__main">
        <Chat />
      </main>
      <footer className="app__footer">
        This demo does not provide a diagnosis or replace a healthcare
        professional. All data is synthetic.
      </footer>
    </div>
  );
}
