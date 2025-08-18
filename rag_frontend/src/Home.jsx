import React, { useState, useEffect } from "react";
import "./App.css";

const TextWindow = ({ title, content }) => {
  return (
    <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-sm mx-auto font-inter">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        {title}
      </h2>

      <div className="text-gray-700 leading-relaxed max-h-80 overflow-y-auto custom-scrollbar">
        {content}
      </div>
    </div>
  );
};

function Home() {
  const [userInput, setUserInput] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [loading, setLoading] = useState(false);
  const [contextData, setContextData] = useState(null);

  useEffect(() => {
    const storedChatLog = localStorage.getItem("chatLog");
    if (storedChatLog) {
      setChatLog(JSON.parse(storedChatLog));
    }
  }, []);

  const handleInputChange = (event) => {
    setUserInput(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!userInput.trim()) return;
    const userMessage = { type: "user", text: userInput };
    setChatLog((prevChatLog) => [...prevChatLog, userMessage]);
    setUserInput("");
    setLoading(true);

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_message: userInput }),
      });

      console.log(response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setContextData(data.context);
      const botMessage = { type: "bot", text: data.bot_response };
      setChatLog((prevChatLog) => [...prevChatLog, botMessage]);
      localStorage.setItem(
        "chatLog",
        JSON.stringify([...chatLog, userMessage, botMessage]),
      );
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = {
        type: "error",
        text: `An error occurred: ${error.message}`,
      };
      setChatLog((prevChatLog) => [...prevChatLog, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>RAG App</h1>

      <div className="main-content-container">
        <div className="chat-section">
          <div className="chat-window custom-scrollbar">
            {chatLog.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                {message.text}
              </div>
            ))}
            {loading && <div className="message bot">Loading...</div>}
          </div>
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              className="input-field"
              value={userInput}
              onChange={handleInputChange}
              placeholder="Type your message..."
            />
            <button type="submit" className="input-button" disabled={loading}>
              Send
            </button>
          </form>
          <div>
            <a
              href={`${window.location.origin}/admin`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <button className="admin-button">Admin</button>
            </a>
          </div>
        </div>

        <div className="text-window-section">
          <TextWindow
            title="Chunk Context"
            content={
              contextData ? contextData : "No context available yet. Ask a question!"
            }
          />
        </div>
      </div>
    </div>
  );
}

export default Home;
