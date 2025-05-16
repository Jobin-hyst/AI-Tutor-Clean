import React, { useEffect, useState, useRef } from 'react';
import { startSession, processPrompt } from './api';
import MonacoEditor from '@monaco-editor/react';
import './App.css';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [codingActive, setCodingActive] = useState(false);
  const [currentProblem, setCurrentProblem] = useState(null);
  const [code, setCode] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    async function initSession() {
      const res = await startSession();
      setSessionId(res.session_id);
      setMessages([{ role: 'bot', text: res.message }]);
    }
    initSession();
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !sessionId) return;
    // If coding is active and user types 'submit' or similar, submit code instead
    if (codingActive && /^(submit|submit code|submit my answer)$/i.test(input.trim())) {
      handleCodeSubmit();
      setInput("");
      return;
    }
    setMessages((msgs) => [...msgs, { role: 'user', text: input }]);
    setLoading(true);
    const res = await processPrompt(sessionId, input);
    // Handle coding question structured response
    if (res.testcases) {
      setCodingActive(true);
      setCurrentProblem(res);
      setMessages((msgs) => [
        ...msgs,
        { role: 'bot', text: res.message },
        { role: 'bot', text: res.testcases.map((tc, i) => `Test Case ${i + 1}:
Input: ${tc.input}
Output: ${tc.output}`).join('\n\n') },
      ]);
      if (res.followup) {
        setMessages((msgs) => [...msgs, { role: 'bot', text: res.followup }]);
      }
    } else {
      setMessages((msgs) => [...msgs, { role: 'bot', text: res.message }]);
      // Only hide the code editor if we are NOT in a coding problem anymore
      if (!codingActive) {
        setCodingActive(false);
        setCurrentProblem(null);
        setCode("");
      }
    }
    setInput("");
    setLoading(false);
  };

  // Submit code for evaluation
  const handleCodeSubmit = async () => {
    if (!code.trim() || !sessionId) return;
    setSubmitting(true);
    setMessages((msgs) => [...msgs, { role: 'user', text: `Submitted code:\n\n${code}` }]);
    // Call backend for code submission
    const res = await fetch('http://localhost:8000/submit-solution', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: code })
    });
    const data = await res.json();
    setMessages((msgs) => [
      ...msgs,
      { role: 'bot', text: `Submission Results: ${data.verdict}\n\n${data.feedback}` }
    ]);
    setSubmitting(false);
  };

  // Responsive split layout for coding
  return (
    <div className="app-container">
      {/* Header with AI Icon */}
      <header className="header">
        <div className="header-content">
          <span className="header-icon">
            <svg width="32" height="32" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="6" y="10" width="26" height="18" rx="9" fill="#ffa500"/>
              <rect x="12" y="16" width="14" height="8" rx="4" fill="#232323"/>
              <circle cx="15.5" cy="20" r="1.5" fill="#ffa500"/>
              <circle cx="22.5" cy="20" r="1.5" fill="#ffa500"/>
              <rect x="17" y="5" width="4" height="7" rx="2" fill="#ffa500"/>
            </svg>
          </span>
          <span className="header-title">AI Tutor Chatbot</span>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className={codingActive ? "main-chat split" : "main-chat"}>
        <div className={codingActive ? "chat-area left" : "chat-area"}>
          {/* Chat messages area */}
          <div className="messages-area">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`message-row ${msg.role}`}
              >
                <span className="message-bubble" style={{ whiteSpace: 'pre-line' }}>{msg.text}</span>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          {/* Input area always visible at the bottom */}
          <div className="input-area">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask anything..."
              className="input-box"
              disabled={loading}
              autoFocus
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="send-btn"
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>
        </div>
        {/* Code editor area, only when coding is active */}
        {codingActive && (
          <div className="code-editor-area" style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            background: 'linear-gradient(90deg, #232323 0%, #181818 100%)',
            borderRadius: '18px',
            boxShadow: '0 8px 32px 0 rgba(0,0,0,0.25)',
            margin: '18px 12px',
            padding: '18px 16px',
            border: '2px solid #ffa500',
            minWidth: 0,
            minHeight: 0,
            flex: 1,
            maxHeight: 'calc(100vh - 60px - 32px - 36px)', // header, footer, margin
            overflow: 'hidden',
          }}>
            <div className="code-editor-header" style={{
              fontWeight: 600,
              color: '#ffa500',
              marginBottom: 10,
              fontSize: '1.1rem',
              letterSpacing: 0.5,
            }}>Write your code below:</div>
            <MonacoEditor
              height="100%"
              width="100%"
              language={currentProblem?.language || 'python'}
              theme="vs-dark"
              value={code}
              onChange={value => setCode(value || '')}
              options={{
                fontSize: 16,
                fontFamily: 'Fira Mono, Menlo, Monaco, Consolas, monospace',
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                wordWrap: 'on',
                automaticLayout: true,
                lineNumbers: 'on',
                roundedSelection: true,
                cursorBlinking: 'smooth',
                scrollbar: { vertical: 'auto', horizontal: 'auto' },
                formatOnPaste: true,
                formatOnType: true,
                tabSize: 4,
                padding: { top: 16, bottom: 16 },
              }}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        &copy; {new Date().getFullYear()} AI Tutor Chatbot. All rights reserved.
      </footer>
    </div>
  );
}

export default App;
