import React, { useEffect, useState, useRef } from 'react'
import { useParams } from 'react-router-dom'
import api from '../services/api'

export default function Session(){
  const { id } = useParams()
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [pdfs, setPdfs] = useState([])
  const fileRef = useRef()

  const load = async ()=>{
    const sres = await api.get(`/sessions/${id}`)
    setSession(sres.session)
    const m = await api.get(`/messages/${id}`)
    setMessages(m.messages || [])
    const p = await api.get(`/pdfs/session/${id}`)
    setPdfs(p.pdfs || [])
  }

  useEffect(()=>{ load() }, [id])

  const send = async (e)=>{
    e.preventDefault()
    await api.post(`/messages/${id}`, { text, role: 'user' })
    setText('')
    load()
  }

  const upload = async (e)=>{
    e.preventDefault()
    if(!fileRef.current.files.length) return
    const form = new FormData()
    form.append('file', fileRef.current.files[0])
    await api.postForm(`/pdfs/upload/${id}`, form)
    fileRef.current.value = null
    load()
  }

  const download = (pdf)=>{
    window.open(`/api/pdfs/download/${pdf._id}`)
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-1 bg-white p-4 rounded shadow">
        <h3 className="font-semibold mb-2">Session</h3>
        {session && <div>
          <div className="font-medium">{session.title}</div>
          <div className="text-sm text-slate-500">Created: {new Date(session.created_at).toLocaleString()}</div>
        </div>}
        <form onSubmit={upload} className="mt-4 space-y-2">
          <input type="file" accept="application/pdf" ref={fileRef} />
          <div>
            <button className="bg-indigo-600 text-white px-3 py-1 rounded">Upload PDF</button>
          </div>
        </form>
        <div className="mt-4">
          <h4 className="font-semibold">PDFs</h4>
          <div className="space-y-2 mt-2">
            {pdfs.map(p => (
              <div key={p._id} className="flex items-center justify-between border p-2 rounded">
                <div className="text-sm">{p.originalname}</div>
                <div className="flex gap-2">
                  <button onClick={()=>download(p)} className="text-indigo-600 text-sm">Download</button>
                </div>
              </div>
            ))}
            {pdfs.length===0 && <div className="text-slate-500">No PDFs</div>}
          </div>
        </div>
      </div>
      <div className="md:col-span-2 bg-white p-4 rounded shadow">
        <h3 className="font-semibold mb-2">Messages</h3>
        <div className="space-y-3 max-h-[50vh] overflow-auto p-2 border rounded">
          {messages.map(m => (
            <div key={m._id} className={`p-2 rounded ${m.role==='user' ? 'bg-slate-100' : 'bg-indigo-50'}`}>
              <div className="text-sm text-slate-600">{m.role}</div>
              <div>{m.text}</div>
            </div>
          ))}
        </div>
        <form onSubmit={send} className="mt-4 flex gap-2">
          <input value={text} onChange={e=>setText(e.target.value)} className="flex-1 border p-2 rounded" placeholder="Type a message" />
          <button className="bg-green-600 text-white px-4 py-2 rounded">Send</button>
        </form>
      </div>
    </div>
  )
}
