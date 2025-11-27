import React, { useEffect, useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Send,
  Paperclip,
  FileText,
  Download,
  ChevronLeft,
  Bot,
  User,
  Loader2,
  FileUp,
  Sparkles
} from 'lucide-react'

export default function Session() {
  const { id } = useParams()
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [pdfs, setPdfs] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const fileRef = useRef()
  const messagesEndRef = useRef(null)

  const load = async () => {
    try {
      const [sRes, mRes, pRes] = await Promise.all([
        api.get(`/sessions/${id}`),
        api.get(`/messages/${id}`),
        api.get(`/pdfs/session/${id}`)
      ])

      if (sRes) setSession(sRes.session)
      if (mRes) setMessages(mRes.messages || [])
      if (pRes) setPdfs(pRes.pdfs || [])
    } catch (e) {
      console.error("Error loading session data:", e)
    }
  }

  useEffect(() => { load() }, [id])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return

    const tempMsg = { _id: Date.now(), role: 'user', text: messageText }
    setMessages(prev => [...prev, tempMsg])
    setLoading(true)

    try {
      await api.post(`/messages/${id}`, { text: messageText, role: 'user' })
      await load()
    } catch (e) {
      console.error("Error sending message:", e)
    } finally {
      setLoading(false)
    }
  }

  const send = async (e) => {
    e.preventDefault()
    await sendMessage(text)
    setText('')
  }

  const summarize = () => {
    sendMessage("Please provide a detailed financial summary of the uploaded documents, including key financial data and insights.")
  }

  const upload = async (e) => {
    e.preventDefault()
    if (!fileRef.current.files.length) return

    setUploading(true)
    const form = new FormData()
    form.append('file', fileRef.current.files[0])

    try {
      await api.postForm(`/pdfs/upload/${id}`, form)
      fileRef.current.value = null
      await load()
    } catch (e) {
      console.error("Error uploading PDF:", e)
    } finally {
      setUploading(false)
    }
  }

  const download = (pdf) => {
    window.open(`/api/pdfs/download/${pdf._id}`)
  }

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900">
      {/* Sidebar */}
      <aside className="w-80 bg-white border-r border-slate-200 flex flex-col shadow-sm z-10">
        <div className="p-6 border-b border-slate-100">
          <Link to="/dashboard" className="inline-flex items-center text-sm text-slate-500 hover:text-indigo-600 mb-4 transition-colors">
            <ChevronLeft className="w-4 h-4 mr-1" />
            Back to Dashboard
          </Link>
          <h1 className="text-xl font-bold text-slate-800 truncate" title={session?.title}>
            {session?.title || 'Loading...'}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            {session ? new Date(session.created_at).toLocaleDateString() : ''}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Summarize Button */}
          <button
            onClick={summarize}
            disabled={loading || pdfs.length === 0}
            className="w-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 font-medium py-2.5 px-4 rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mb-4"
          >
            <Sparkles className="w-4 h-4" /> Generate Summary
          </button>

          <div className="flex items-center justify-between mb-2">
            <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">Documents</h2>
            <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">{pdfs.length}</span>
          </div>

          <div className="space-y-2">
            {pdfs.map(p => (
              <div key={p._id} className="group flex items-center justify-between p-3 bg-slate-50 hover:bg-indigo-50 rounded-lg border border-slate-100 hover:border-indigo-100 transition-all">
                <div className="flex items-center overflow-hidden">
                  <FileText className="w-5 h-5 text-indigo-500 mr-3 flex-shrink-0" />
                  <span className="text-sm text-slate-700 truncate" title={p.originalname}>{p.originalname}</span>
                </div>
                <button
                  onClick={() => download(p)}
                  className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-white rounded-md transition-colors opacity-0 group-hover:opacity-100"
                  title="Download PDF"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            ))}
            {pdfs.length === 0 && (
              <div className="text-center py-8 text-slate-400 text-sm border-2 border-dashed border-slate-100 rounded-lg">
                No documents uploaded
              </div>
            )}
          </div>
        </div>

        <div className="p-4 border-t border-slate-100 bg-slate-50/50">
          <form onSubmit={upload}>
            <input
              type="file"
              accept="application/pdf"
              ref={fileRef}
              className="hidden"
              onChange={upload}
            />
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              disabled={uploading}
              className="w-full flex items-center justify-center gap-2 bg-white border border-slate-200 hover:border-indigo-300 text-slate-700 hover:text-indigo-700 py-2.5 px-4 rounded-lg transition-all shadow-sm hover:shadow font-medium text-sm"
            >
              {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileUp className="w-4 h-4" />}
              {uploading ? 'Uploading...' : 'Upload PDF'}
            </button>
          </form>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col bg-slate-50/30">
        {/* Chat Header */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center px-6 justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-sm font-medium text-slate-600">AI Assistant Active</span>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 opacity-50">
              <Bot className="w-16 h-16 mb-4" />
              <p className="text-lg font-medium">Start the conversation</p>
              <p className="text-sm">Ask questions about your uploaded documents</p>
            </div>
          )}

          {messages.map((m, idx) => (
            <div
              key={m._id || idx}
              className={`flex gap-4 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.role !== 'user' && (
                <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 border border-indigo-200">
                  <Bot className="w-5 h-5 text-indigo-600" />
                </div>
              )}

              <div
                className={`max-w-3xl rounded-2xl px-6 py-4 shadow-sm ${m.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-br-none'
                    : 'bg-white text-slate-800 border border-slate-100 rounded-bl-none w-full'
                  }`}
              >
                {m.role === 'ai' ? (
                  (() => {
                    try {
                      // Try to parse JSON if it's a string
                      const data = typeof m.text === 'string' ? JSON.parse(m.text) : m.text;

                      // Check if it has the expected structure
                      if (data && data.summary && data.financial_data) {
                        return (
                          <div className="space-y-6">
                            {/* Executive Summary */}
                            <div className="bg-indigo-50/50 p-4 rounded-xl border border-indigo-100">
                              <h3 className="text-sm font-semibold text-indigo-900 uppercase tracking-wide mb-2 flex items-center gap-2">
                                <Bot className="w-4 h-4" /> Executive Summary
                              </h3>
                              <p className="text-slate-700 leading-relaxed text-sm">{data.summary}</p>
                            </div>

                            {/* Financial Data Grid */}
                            <div className="grid grid-cols-2 gap-3">
                              {Object.entries(data.financial_data).map(([key, value]) => (
                                <div key={key} className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                                  <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">{key.replace(/_/g, ' ')}</div>
                                  <div className="font-semibold text-slate-900">{value}</div>
                                </div>
                              ))}
                            </div>

                            {/* Key Insights */}
                            {data.key_insights && data.key_insights.length > 0 && (
                              <div>
                                <h4 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
                                  <FileText className="w-4 h-4 text-indigo-500" /> Key Insights
                                </h4>
                                <ul className="space-y-2">
                                  {data.key_insights.map((insight, i) => (
                                    <li key={i} className="flex gap-3 text-sm text-slate-700 bg-white p-3 rounded-lg border border-slate-100 shadow-sm">
                                      <span className="text-indigo-500 font-bold">•</span>
                                      {insight}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Detailed Sections */}
                            {data.sections && data.sections.map((section, i) => (
                              <div key={i} className="border-t border-slate-100 pt-4">
                                <h4 className="font-semibold text-slate-800 mb-2">{section.title}</h4>
                                <div className="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">
                                  {section.content}
                                </div>
                              </div>
                            ))}
                          </div>
                        );
                      }
                      // Fallback to markdown if not structured
                      return (
                        <div className="prose prose-sm max-w-none prose-indigo prose-p:leading-relaxed prose-headings:font-semibold prose-a:text-indigo-600">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {m.text || ''}
                          </ReactMarkdown>
                        </div>
                      );
                    } catch (e) {
                      // Fallback on parse error
                      return (
                        <div className="prose prose-sm max-w-none prose-indigo prose-p:leading-relaxed prose-headings:font-semibold prose-a:text-indigo-600">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {m.text || ''}
                          </ReactMarkdown>
                        </div>
                      );
                    }
                  })()
                ) : (
                  <div className="whitespace-pre-wrap leading-relaxed">{m.text}</div>
                )}
              </div>

              {m.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0 border border-slate-300">
                  <User className="w-5 h-5 text-slate-500" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-4 justify-start animate-pulse">
              <div className="w-8 h-8 rounded-full bg-indigo-50 flex items-center justify-center border border-indigo-100">
                <Bot className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="bg-white border border-slate-100 rounded-2xl rounded-bl-none px-6 py-4 shadow-sm flex items-center gap-2">
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-6 bg-white border-t border-slate-200">
          <div className="max-w-4xl mx-auto relative">
            <form onSubmit={send} className="relative flex items-center gap-2">
              <input
                value={text}
                onChange={e => setText(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 block p-4 pl-4 pr-12 shadow-sm transition-all placeholder:text-slate-400"
                placeholder="Ask a question about your documents..."
                disabled={loading}
              />
              <button
                type="submit"
                disabled={!text.trim() || loading}
                className="absolute right-2 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              </button>
            </form>
            <p className="text-center text-xs text-slate-400 mt-3">
              AI can make mistakes. Please verify important information from the original documents.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
