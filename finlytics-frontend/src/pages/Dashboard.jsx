import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'

export default function Dashboard(){
  const [sessions, setSessions] = useState([])
  const [title, setTitle] = useState('')

  const load = async ()=>{
    const res = await api.get('/sessions')
    setSessions(res.sessions || [])
  }

  useEffect(()=>{ load() }, [])

  const create = async (e)=>{
    e.preventDefault()
    const res = await api.post('/sessions', { title: title || 'New Chat' })
    setTitle('')
    load()
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-1 bg-white p-4 rounded shadow">
        <h3 className="font-semibold mb-2">Create Session</h3>
        <form onSubmit={create} className="space-y-2">
          <input value={title} onChange={e=>setTitle(e.target.value)} placeholder="Session title" className="w-full border p-2 rounded" />
          <button className="bg-green-600 text-white px-3 py-1 rounded">Create</button>
        </form>
      </div>
      <div className="md:col-span-2 bg-white p-4 rounded shadow">
        <h3 className="font-semibold mb-2">Your Sessions</h3>
        <div className="space-y-2">
          {sessions.length===0 && <div className="text-slate-500">No sessions yet</div>}
          {sessions.map(s => (
            <div key={s._id} className="flex items-center justify-between border p-2 rounded">
              <div>
                <div className="font-medium">{s.title}</div>
                <div className="text-sm text-slate-500">{new Date(s.updated_at).toLocaleString()}</div>
              </div>
              <div className="flex gap-2">
                <Link to={`/session/${s._id}`} className="text-indigo-600">Open</Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
