import { useState, useRef, useEffect } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return

    const userMsg: Message = { role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, user_id: 'user1' }),
      })
      const data = await res.json()
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Banking Assistant</h1>
      </header>

      <div style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.empty}>
            <p style={styles.emptyTitle}>Welcome to Banking Assistant</p>
            <p style={styles.emptyHint}>
              Try asking: &quot;What is my account balance?&quot;, &quot;Show my
              recent transactions&quot;, or &quot;Pay $50 to Bob Smith&quot;
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.messageBubble,
              ...(msg.role === 'user' ? styles.userBubble : styles.assistantBubble),
            }}
          >
            <div style={styles.roleLabel}>
              {msg.role === 'user' ? 'You' : 'Assistant'}
            </div>
            <div style={styles.messageText}>{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div style={{ ...styles.messageBubble, ...styles.assistantBubble }}>
            <div style={styles.roleLabel}>Assistant</div>
            <div style={styles.messageText}>Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputArea}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about your account, transactions, or payments..."
          disabled={loading}
        />
        <button style={styles.button} onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    background: '#f5f5f5',
  },
  header: {
    padding: '1rem 1.5rem',
    background: '#1a56db',
    color: '#fff',
    borderBottom: '1px solid #ddd',
  },
  title: { margin: 0, fontSize: '1.25rem', fontWeight: 600 },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  empty: { textAlign: 'center', marginTop: '4rem', color: '#888' },
  emptyTitle: { fontSize: '1.2rem', fontWeight: 600, color: '#555' },
  emptyHint: { fontSize: '0.95rem', maxWidth: '400px', margin: '0.5rem auto' },
  messageBubble: {
    maxWidth: '75%',
    padding: '0.75rem 1rem',
    borderRadius: '12px',
    lineHeight: 1.5,
    whiteSpace: 'pre-wrap' as const,
  },
  userBubble: {
    alignSelf: 'flex-end',
    background: '#1a56db',
    color: '#fff',
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    background: '#fff',
    border: '1px solid #e0e0e0',
    color: '#333',
  },
  roleLabel: { fontSize: '0.75rem', fontWeight: 700, marginBottom: '0.25rem', opacity: 0.7 },
  messageText: { fontSize: '0.95rem' },
  inputArea: {
    display: 'flex',
    padding: '1rem 1.5rem',
    gap: '0.75rem',
    borderTop: '1px solid #ddd',
    background: '#fff',
  },
  input: {
    flex: 1,
    padding: '0.75rem 1rem',
    fontSize: '1rem',
    border: '1px solid #ccc',
    borderRadius: '8px',
    outline: 'none',
  },
  button: {
    padding: '0.75rem 1.5rem',
    fontSize: '1rem',
    background: '#1a56db',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: 600,
  },
}

export default App
