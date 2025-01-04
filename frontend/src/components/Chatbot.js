import React, { useState } from "react";

const Chatbot = () => {
  const [userInput, setUserInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error state

  const handleInputChange = (event) => {
    setUserInput(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true); // Set loading to true
    setError(null); // Reset error state

    try {
      const response = await sendMessageToChatbot(userInput);
      setChatHistory([...chatHistory, { user: userInput, bot: response }]);
      setUserInput("");
    } catch (err) {
      setError("Failed to send message. Please try again."); // Set error message
    } finally {
      setLoading(false); // Reset loading state
    }
  };

  const sendMessageToChatbot = async (message) => {
    const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
    });

    if (!response.ok) {
        throw new Error("Network response was not ok");
    }

    const data = await response.json();
    return data.reply; // Assuming the response contains a 'reply' field
  };

  return (
    <div className="chatbot-container">
      <h2>Chat with AGI</h2>
      <div className="chat-history">
        {chatHistory.map((chat, index) => (
          <div key={index}>
            <strong>You:</strong> {chat.user}
            <br />
            <strong>AGI:</strong> {chat.bot}
            <br />
          </div>
        ))}
      </div>
      {loading && <p>Loading...</p>} {/* Loading indicator */}
      {error && <p style={{ color: 'red' }}>{error}</p>} {/* Error message */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={userInput}
          onChange={handleInputChange}
          placeholder="Type your message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
};

export default Chatbot;