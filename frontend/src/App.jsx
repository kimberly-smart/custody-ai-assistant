import { useState } from "react";
import "./App.css";

function App() {
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
      formData.append("question", trimmedQuestion);
      formData.append("top_k", "2");

      const response = await fetch("http://127.0.0.1:8000/chat/ask", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Unable to receive an answer from the server.");
      }

      const data = await response.json();

      const assistantMessage = {
        role: "assistant",
        text: data.answer,
        sources: data.sources || [],
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
          text: "Something went wrong while answering your question. Please try again.",
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
            <h2>Custody & Divorce Document Assistant</h2>
            <p>Ask questions based on your uploaded court documents.</p>
          </div>
          <span className="status">Azure RAG Active</span>
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
                  Searching your documents...
                </div>
              </div>
            </div>
          )}
        </section>

        <form className="composer" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Ask about your custody or divorce documents..."
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