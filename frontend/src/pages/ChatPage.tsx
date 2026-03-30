import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { agentApi } from '../api/agent'

interface Message {
  role: 'human' | 'assistant'
  content: string
  loading?: boolean
}

// Genera un thread_id único por sesión de chat
function generateThreadId() {
  return `thread-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
}

// ── Componente de burbuja de mensaje ─────────────────────────────────
function MessageBubble({ message }: { message: Message }) {
  const isHuman = message.role === 'human'

  return (
    <div className={`flex ${isHuman ? 'justify-end' : 'justify-start'} mb-4`}>
      {!isHuman && (
        <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold mr-3 flex-shrink-0 mt-1">
          FS
        </div>
      )}
      <div
        className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isHuman
            ? 'bg-indigo-600 text-white rounded-tr-sm'
            : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm'
        }`}
      >
        {message.loading ? (
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        ) : (
          <p className="whitespace-pre-wrap">{message.content}</p>
        )}
      </div>
      {isHuman && (
        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-xs font-bold ml-3 flex-shrink-0 mt-1">
          Tú
        </div>
      )}
    </div>
  )
}

// ── Sugerencias de preguntas ──────────────────────────────────────────
const SUGGESTIONS = [
  '¿Qué posiciones tengo en mi portfolio?',
  '¿Cuál es el precio actual de AAPL?',
  'Calcula el Sharpe ratio de mi portfolio',
  '¿Cómo está el mercado hoy?',
]

// ── Página principal del Chat ─────────────────────────────────────────
export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        '¡Hola! Soy FinSight, tu analista financiero con IA. Puedo consultar tu portfolio, obtener precios de mercado en tiempo real y calcular métricas de riesgo. ¿En qué puedo ayudarte?',
    },
  ])
  const [input, setInput] = useState('')
  const [threadId] = useState(generateThreadId)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const mutation = useMutation({
    mutationFn: ({ message, threadId }: { message: string; threadId: string }) =>
      agentApi.chat(message, threadId),

    onMutate: ({ message }) => {
      // Añade el mensaje del usuario inmediatamente
      setMessages((prev) => [
        ...prev,
        { role: 'human', content: message },
        { role: 'assistant', content: '', loading: true },
      ])
    },

    onSuccess: (data) => {
      // Reemplaza el mensaje de loading con la respuesta real
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { role: 'assistant', content: data.response },
      ])
    },

    onError: () => {
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: 'assistant',
          content: 'Lo siento, hubo un error procesando tu mensaje. Inténtalo de nuevo.',
        },
      ])
    },
  })

  const handleSend = () => {
    const message = input.trim()
    if (!message || mutation.isPending) return
    setInput('')
    mutation.mutate({ message, threadId })
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Enter envía, Shift+Enter hace salto de línea
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSuggestion = (suggestion: string) => {
    setInput(suggestion)
    inputRef.current?.focus()
  }

  return (
    <Layout>
      <div className="flex flex-col h-[calc(100vh-8rem)]">
        {/* Header del chat */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-bold">
            FS
          </div>
          <div>
            <h2 className="text-sm font-semibold text-gray-900">
              Agente FinSight
            </h2>
            <p className="text-xs text-gray-500">
              Powered by LangGraph · llama-3.3-70b
            </p>
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-green-400" />
            <span className="text-xs text-gray-500">En línea</span>
          </div>
        </div>

        {/* Área de mensajes */}
        <div className="flex-1 overflow-y-auto bg-gray-50 rounded-xl border border-gray-200 p-4">
          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Sugerencias — solo cuando no hay conversación */}
        {messages.length === 1 && (
          <div className="flex gap-2 mt-3 flex-wrap">
            {SUGGESTIONS.map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => handleSuggestion(suggestion)}
                className="text-xs bg-white border border-gray-200 text-gray-600 px-3 py-1.5 rounded-full hover:border-indigo-300 hover:text-indigo-600 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="mt-3 flex gap-3 items-end">
          <div className="flex-1 bg-white border border-gray-200 rounded-xl overflow-hidden focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-transparent transition-all">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Pregunta sobre tu portfolio... (Enter para enviar)"
              rows={1}
              className="w-full px-4 py-3 text-sm resize-none focus:outline-none"
              style={{ maxHeight: '120px' }}
              disabled={mutation.isPending}
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || mutation.isPending}
            className="bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="w-5 h-5"
            >
              <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
            </svg>
          </button>
        </div>
      </div>
    </Layout>
  )
}