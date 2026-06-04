import { useState } from "react";
import "./App.css";

function App() {
  const [mode, setMode] = useState("documents");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! Upload your custody or divorce documents and ask a question about them.",
      sources: [],
    },
  ]);
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || isLoading) {
      return;
    }

    const userMessage = {
      role: "user",
      text: trimmedQuestion,
      sources: [],
    };

    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setQuestion("");
    setIsLoading(true);

    try {
      const formData = new FormData();

      let endpoint = "";
      let assistantText = "";
      let sources = [];

      if (mode === "documents") {
        endpoint = "http://127.0.0.1:8000/chat/ask";

        formData.append("question", trimmedQuestion);
        formData.append("top_k", "2");
      } else {
        endpoint = "http://127.0.0.1:8000/rewrite/message";

        formData.append("message", trimmedQuestion);
        formData.append("tone", "neutral");
      }

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Unable to receive a response from the server.");
      }

      const data = await response.json();

      if (mode === "documents") {
        assistantText = data.answer;
        sources = data.sources || [];
      } else {
        assistantText = data.rewritten_message;
      }

      const assistantMessage = {
        role: "assistant",
        text: assistantText,
        sources: sources,
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ]);
    } catch (error) {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          text:
            mode === "documents"
              ? "Something went wrong while answering your question. Please try again."
              : "Something went wrong while rewriting your message. Please try again.",
          sources: [],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">C</div>
          <div>
            <h1>CustodyAI</h1>
            <p>Document Assistant</p>
          </div>
        </div>

        <button className="new-chat-button">+ New chat</button>

        <div className="sidebar-section">
          <h2>Documents</h2>
          <div className="document-card">
            <span className="document-icon">PDF</span>
            <div>
              <strong>Uploaded Documents</strong>
              <p>Source-grounded answers</p>
            </div>
          </div>
        </div>

        <div className="disclaimer">
          <strong>Important</strong>
          <p>
            This tool provides document-based information, not legal advice.
          </p>
        </div>
      </aside>

      <main className="chat-panel">
        <header className="chat-header">
          <div>
            <h2>Custody & Divorce Assistant</h2>
            <p>
              {mode === "documents"
                ? "Ask questions based on your uploaded court documents."
                : "Rewrite emotional messages into calm co-parenting communication."}
            </p>
          </div>

          <div className="header-controls">
            <div className="mode-switch">
              <button
                type="button"
                className={mode === "documents" ? "mode-button active" : "mode-button"}
                onClick={() => setMode("documents")}
              >
                Ask Documents
              </button>

              <button
                type="button"
                className={mode === "rewrite" ? "mode-button active" : "mode-button"}
                onClick={() => setMode("rewrite")}
              >
                Rewrite Message
              </button>
            </div>

            <span className="status">
              {mode === "documents" ? "Azure RAG Active" : "Rewrite Mode"}
            </span>
          </div>
        </header>

        <section className="messages">
          {messages.map((message, index) => (
            <div
              className={`message-row ${message.role}`}
              key={`${message.role}-${index}`}
            >
              <div className="avatar">
                {message.role === "assistant" ? "AI" : "You"}
              </div>

              <div className="message-content">
                <div className="message-bubble">{message.text}</div>

                {message.sources.length > 0 && (
                  <div className="sources">
                    {message.sources.map((source) => (
                      <div className="source-chip" key={source.chunk_id}>
                        Source: {source.filename}, Page {source.page_number}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message-row assistant">
              <div className="avatar">AI</div>
              <div className="message-content">
                <div className="message-bubble loading">
                  {mode === "documents"
                  ? "Searching your documents..."
                  : "Rewriting your message..."}
                </div>
              </div>
            </div>
          )}
        </section>

        <form className="composer" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder={
              mode === "documents"
                ? "Ask about your custody or divorce documents..."
                : "Paste a message and describe the tone, e.g. 'Rewrite this firmly: ...'"
            }
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !question.trim()}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;