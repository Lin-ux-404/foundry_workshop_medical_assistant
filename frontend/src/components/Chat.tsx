import { useEffect, useRef, useState, type FormEvent } from "react";
import { LoaderCircle, Send, Sparkles, X } from "lucide-react";
import { sendChat } from "../api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setError(null);
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const reply = await sendChat(text);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function clearChat() {
    setMessages([]);
    setError(null);
  }

  return (
    <div className="chat">
      <div className="chat__header">
        <div className="chat__identity">
          <span className="chat__icon" aria-hidden="true">
            <Sparkles size={19} strokeWidth={2} />
          </span>
          <div>
            <h2>AI health assistant</h2>
            <span className="chat__status">Online and ready to help</span>
          </div>
        </div>
        <button
          className="chat__clear"
          type="button"
          onClick={clearChat}
          disabled={messages.length === 0 && !error}
          aria-label="Clear conversation"
          title="Clear conversation"
        >
          <X size={18} />
        </button>
      </div>

      <div className="chat__messages" aria-live="polite">
        {messages.length === 0 ? (
          <div className="chat__empty">
            <span className="chat__empty-icon" aria-hidden="true">
              <Sparkles size={30} strokeWidth={1.8} />
            </span>
            <h3>How can I help you today?</h3>
            <p>
              Describe how you are feeling or ask a general health question to
              get started.
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`message message--${message.role}`}
            >
              <span className="message__label">
                {message.role === "user" ? "You" : "Assistant"}
              </span>
              <div className={`bubble bubble--${message.role}`}>
                {message.content}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="message message--assistant">
            <span className="message__label">Assistant</span>
            <div className="bubble bubble--assistant bubble--typing">
              <span />
              <span />
              <span />
              <span className="sr-only">Thinking</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat__composer">
        {error && (
          <div className="chat__error" role="alert">
            {error}
          </div>
        )}
        <form className="chat__form" onSubmit={handleSend}>
          <input
            className="chat__input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={loading}
            aria-label="Message"
          />
          <button
            className="chat__send"
            type="submit"
            disabled={loading || !input.trim()}
            aria-label={loading ? "Waiting for response" : "Send message"}
          >
            {loading ? (
              <LoaderCircle size={20} className="spin" />
            ) : (
              <Send size={19} />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
