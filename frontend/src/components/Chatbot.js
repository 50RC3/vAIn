import React, { useState, useCallback, useEffect } from "react";
import { createWebSocketConnection } from '../utils/websocket';

import { NetworkError, APIError, getErrorMessage } from '../utils/errors';

// Add TypeScript types
/**
 * @typedef {Object} ChatMessage
 * @property {string} id
 * @property {string} user
 * @property {string} bot
 * @property {boolean} rated
 */

/**
 * @typedef {'safe' | 'creative' | 'precise'} ChatMode
 */

const COMMANDS = {
  '/help': 'Shows available commands',
  '/clear': 'Clears chat history',
  '/mode': 'Changes chat mode (safe|creative|precise)',
};

const Chatbot = () => {
  const [userInput, setUserInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error state
  const [mode, setMode] = useState("safe");
  const [lastMessageId, setLastMessageId] = useState(null);

  const handleInputChange = (event) => {
    setUserInput(event.target.value);
  };

const sendMessageToChatbot = async (message) => {
    const onMessage = (message) => {
        // Handle incoming messages from the chatbot
    };

    const onError = (errorMessage) => {
        setError(errorMessage);
    };

    const ws = createWebSocketConnection("ws://localhost:8000/chat", onMessage, onError);

    try {
    const response = await fetch("http://localhost:8000/chat", { 

        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message, mode }), // Include mode in request
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.message || `Server error: ${response.status}`,
          response.status
        );
      }

      const data = await response.json();
      if (!data.reply) {
        throw new Error('Invalid response format');
      }

      return data.reply;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      if (error.name === 'TypeError' || error.message.includes('fetch')) {
        throw new NetworkError();
      }
      throw new Error('Failed to process message');
    }
  };

  // Add persistence
  useEffect(() => {
    const savedHistory = localStorage.getItem('chatHistory');
    if (savedHistory) {
      setChatHistory(JSON.parse(savedHistory));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
  }, [chatHistory]);

  // Add command handling
  const handleCommand = (command) => {
    const [cmd, ...args] = command.split(' ');
    
    switch (cmd.toLowerCase()) {
      case '/help':
        const helpMessage = Object.entries(COMMANDS)
          .map(([cmd, desc]) => `${cmd}: ${desc}`)
          .join('\n');
        setChatHistory(prev => [...prev, {
          id: Date.now().toString(),
          user: command,
          bot: helpMessage,
          rated: true
        }]);
        break;
      
      case '/clear':
        setChatHistory([]);
        localStorage.removeItem('chatHistory');
        break;
      
      case '/mode':
        const newMode = args[0];
        if (['safe', 'creative', 'precise'].includes(newMode)) {
          setMode(newMode);
          return true;
        }
        return false;
      
      default:
        return false;
    }
    return true;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!userInput.trim()) return;

    // Check for commands
    if (userInput.startsWith('/')) {
      const handled = handleCommand(userInput);
      if (handled) {
        setUserInput("");
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      const response = await sendMessageToChatbot(userInput);
      const messageId = Date.now().toString();
      setChatHistory(prev => [...prev, { 
        id: messageId, 
        user: userInput, 
        bot: response,
        rated: false 
      }]);
      setLastMessageId(messageId);
      setUserInput("");
    } catch (err) {
      setError(getErrorMessage(err));
      console.error('Chat error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRating = useCallback(async (messageId, rating, comment = "") => {
    if (loading) return;
    
    const targetMessage = chatHistory.find(msg => msg.id === messageId);
    if (!targetMessage || targetMessage.rated) return;
    
    try {
      setLoading(true);
      setError(null);
    const response = await fetch("http://localhost:8000/rate", { 

        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messageId, rating, comment }),
      });

      if (!response.ok) {
        throw new APIError('Failed to submit rating', response.status);
      }

      setChatHistory(prev =>
        prev.map(msg =>
          msg.id === messageId ? { ...msg, rated: true } : msg
        )
      );
    } catch (err) {
      setError(getErrorMessage(err));
      console.error('Rating error:', err);
    } finally {
      setLoading(false);
    }
  }, [chatHistory, loading]);

  // Improve message rendering with accessibility
  const renderMessage = useCallback((chat, index) => (
    <div key={chat.id || index} className="message-container" role="log" aria-live="polite">
      <div className="user-message" role="article">
        <strong>You:</strong> {chat.user}
      </div>
      <div className="bot-message" role="article">
        <strong>AGI:</strong> {chat.bot}
        {!chat.rated && (
          <div className="message-actions" role="group" aria-label="Message rating">
            <button 
              onClick={() => handleRating(chat.id, 1)}
              disabled={loading}
              aria-label="Rate message negatively"
            >👎</button>
            <button 
              onClick={() => handleRating(chat.id, 5)}
              disabled={loading}
              aria-label="Rate message positively"
            >👍</button>
          </div>
        )}
      </div>
    </div>
  ), [loading, handleRating]);

  return (
    <div className="chatbot-container" role="main">
      <div className="chatbot-header">
        <h2>Chat with AGI</h2>
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="safe">Safe Mode</option>
          <option value="creative">Creative Mode</option>
          <option value="precise">Precise Mode</option>
        </select>
      </div>
      
      <div className="chat-history">
        {chatHistory.map((chat, index) => renderMessage(chat, index))}
      </div>
      
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <form onSubmit={handleSubmit} aria-label="Chat input">
        <input
          type="text"
          value={userInput}
          onChange={handleInputChange}
          placeholder="Type a message or command (e.g., /help)"
          aria-label="Message input"
        />
        <button type="submit" disabled={loading || !userInput.trim()}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default Chatbot;
