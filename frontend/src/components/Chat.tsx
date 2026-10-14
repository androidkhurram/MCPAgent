import { useEffect, useRef, useState, type FormEvent } from 'react'
import type { ChatMessage } from '../api/client'

interface ChatProps {
  messages: ChatMessage[]
  loading: boolean
  statusText?: string | null
  onSend: (text: string) => void
  emptyHint?: string
  ariaLabel?: string
  placeholder?: string
}

export function Chat({
  messages,
  loading,
  statusText,
  onSend,
  emptyHint,
  ariaLabel = 'Chat',
  placeholder = 'Describe what you need…',
}: ChatProps) {
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading, statusText])

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const text = input.trim()
    if (!text || loading) return
    onSend(text)
    setInput('')
  }

  return (
    <section className="chat" aria-label={ariaLabel}>
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>
              {emptyHint ? (
                <>
                  Ask in natural language — for example: <em>{emptyHint}</em>
                </>
              ) : (
                <>
                  Ask in natural language — for example:{' '}
                  <em>
                    “Dubai Mar 10–15, king room near Burj Khalifa, under $250/night”
                  </em>
                </>
              )}
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`bubble ${message.role}`}
            >
              <span className="role-label">
                {message.role === 'user' ? 'You' : 'Agent'}
              </span>
              <p>{message.content}</p>
            </div>
          ))
        )}
        {loading ? (
          <div className="bubble assistant status">
            <span className="role-label">Agent</span>
            <p>{statusText || 'Thinking…'}</p>
          </div>
        ) : null}
        <div ref={bottomRef} />
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <label className="sr-only" htmlFor="chat-input">
          Your travel request
        </label>
        <textarea
          id="chat-input"
          rows={2}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={placeholder}
          disabled={loading}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSubmit(e)
            }
          }}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </section>
  )
}
