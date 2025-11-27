import React, { useEffect, useState } from 'react'
import api from '../services/api'
import Card from '../components/Card'
import Button from '../components/Button'

export default function Analysis(){
  const [sessions, setSessions] = useState([])
  const [selectedSession, setSelectedSession] = useState(null)
  const [pdfs, setPdfs] = useState([])
  const [selectedPdfs, setSelectedPdfs] = useState(new Set())
  const [analysis, setAnalysis] = useState(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)

  useEffect(()=>{ loadSessions() }, [])

  async function loadSessions(){
    const res = await api.get('/sessions')
    setSessions(res.sessions || [])
  }

  async function loadPdfsForSession(sid){
    const res = await api.get(`/pdfs/session/${sid}`)
    setPdfs(res.pdfs || [])
  }

  function togglePdf(id){
    const s = new Set(selectedPdfs)
    if(s.has(id)) s.delete(id); else s.add(id)
    setSelectedPdfs(s)
  }

  async function analyze(){
    if(selectedPdfs.size===0) return alert('Select PDFs')
    const pdf_meta_ids = Array.from(selectedPdfs)
    const res = await api.post('/analysis/analyze', { pdf_meta_ids })
    setAnalysis(res.analysis)
  }

  async function ask(){
    if(!question) return
    const pdf_meta_ids = selectedPdfs.size ? Array.from(selectedPdfs) : undefined
    const res = await api.post('/analysis/ask', { question, pdf_meta_ids })
    setAnswer(res.response)
  }

  return (
    <div className="grid md:grid-cols-3 gap-6">
      <div className="md:col-span-1">
        <Card>
          <h4 className="font-semibold mb-2">Sessions</h4>
          <div className="space-y-2">
            {sessions.map(s=> (
              <div key={s._id} className={`p-2 border rounded cursor-pointer ${selectedSession===s._id ? 'bg-indigo-50':''}`} onClick={()=>{ setSelectedSession(s._id); loadPdfsForSession(s._id) }}>{s.title}</div>
            ))}
          </div>
        </Card>
        <Card className="mt-4">
          <h4 className="font-semibold mb-2">Actions</h4>
          <div className="flex gap-2">
            <Button onClick={analyze}>Analyze</Button>
          </div>
        </Card>
      </div>
      <div className="md:col-span-2">
        <Card>
          <h4 className="font-semibold mb-2">PDFs</h4>
          <div className="space-y-2 max-h-48 overflow-auto">
            {pdfs.map(p=> (
              <div key={p._id} className="flex items-center justify-between border p-2 rounded">
                <div>
                  <div className="font-medium">{p.originalname}</div>
                  <div className="text-sm text-slate-500">{p.size} bytes</div>
                </div>
                <div>
                  <input type="checkbox" checked={selectedPdfs.has(p._id)} onChange={()=>togglePdf(p._id)} />
                </div>
              </div>
            ))}
            {pdfs.length===0 && <div className="text-slate-500">No PDFs for selected session</div>}
          </div>
        </Card>

        <Card className="mt-4">
          <h4 className="font-semibold mb-2">Analysis Result</h4>
          <pre className="whitespace-pre-wrap text-sm bg-slate-50 p-3 rounded">{analysis ? JSON.stringify(analysis, null, 2) : 'No analysis yet'}</pre>
        </Card>

        <Card className="mt-4">
          <h4 className="font-semibold mb-2">Ask Question</h4>
          <textarea value={question} onChange={e=>setQuestion(e.target.value)} className="w-full border p-2 rounded" rows={3} />
          <div className="mt-2 flex gap-2">
            <Button onClick={ask}>Ask</Button>
          </div>
          <div className="mt-2">
            <h5 className="font-semibold">Answer</h5>
            <pre className="whitespace-pre-wrap text-sm bg-slate-50 p-3 rounded">{answer ? JSON.stringify(answer, null, 2) : 'No answer yet'}</pre>
          </div>
        </Card>
      </div>
    </div>
  )
}
