import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api, { clearToken } from '../services/api'
import { Plus, MessageSquare, LogOut, Search, Clock, ChevronRight } from 'lucide-react'

export default function Dashboard() {
  const [sessions, setSessions] = useState([])
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(true)
  const nav = useNavigate()

  const load = async () => {
    try {
      const res = await api.get('/sessions')
      setSessions(res.sessions || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const create = async (e) => {
    e.preventDefault()
    if (!title.trim()) return
    try {
      const res = await api.post('/sessions', { title: title || 'New Chat' })
      setTitle('')
      load()
      nav(`/session/${res.id}`)
    } catch (e) {
      console.error(e)
    }
  }

  const logout = () => {
    clearToken()
    nav('/login')
  }

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      {/* Navbar */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">F</span>
              </div>
              <span className="text-xl font-bold text-slate-800 tracking-tight">Finlytics</span>
            </div>
            <div className="flex items-center">
              <button
                onClick={logout}
                className="text-slate-500 hover:text-red-600 transition-colors p-2 rounded-full hover:bg-red-50"
                title="Sign out"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-500 mt-1">Manage your financial analysis sessions</p>
        </div>

        {/* Create Session Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 mb-8">
          <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Plus className="w-5 h-5 text-indigo-600" /> Start New Analysis
          </h2>
          <form onSubmit={create} className="flex gap-4">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MessageSquare className="h-5 w-5 text-slate-400" />
              </div>
              <input
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="e.g., Q3 Financial Report Analysis"
                className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all outline-none"
              />
            </div>
            <button
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-md shadow-indigo-200 flex items-center gap-2 whitespace-nowrap"
            >
              Create Session <ChevronRight className="w-4 h-4" />
            </button>
          </form>
        </div>

        {/* Sessions Grid */}
        <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-slate-400" /> Recent Sessions
        </h3>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-slate-100 rounded-2xl animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sessions.length === 0 && (
              <div className="col-span-full text-center py-12 bg-white rounded-2xl border border-dashed border-slate-200">
                <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Search className="w-8 h-8 text-slate-300" />
                </div>
                <p className="text-slate-500 font-medium">No sessions found</p>
                <p className="text-slate-400 text-sm">Create a new session to get started</p>
              </div>
            )}

            {sessions.map(s => (
              <Link
                to={`/session/${s._id}`}
                key={s._id}
                className="group bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md hover:border-indigo-100 transition-all flex flex-col justify-between h-40"
              >
                <div>
                  <div className="flex items-start justify-between mb-2">
                    <div className="w-10 h-10 bg-indigo-50 rounded-lg flex items-center justify-center group-hover:bg-indigo-100 transition-colors">
                      <MessageSquare className="w-5 h-5 text-indigo-600" />
                    </div>
                    <span className="text-xs text-slate-400 bg-slate-50 px-2 py-1 rounded-full border border-slate-100">
                      {new Date(s.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h4 className="font-semibold text-slate-800 line-clamp-1 group-hover:text-indigo-600 transition-colors">
                    {s.title}
                  </h4>
                  <p className="text-sm text-slate-500 mt-1 line-clamp-1">
                    Click to view analysis...
                  </p>
                </div>
                <div className="flex items-center text-sm text-indigo-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity transform translate-y-2 group-hover:translate-y-0">
                  Open Session <ArrowRight className="w-4 h-4 ml-1" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function ArrowRight({ className }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M5 12h14" />
      <path d="m12 5 7 7-7 7" />
    </svg>
  )
}
