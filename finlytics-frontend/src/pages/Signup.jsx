import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function Signup(){
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const nav = useNavigate()

  const submit = async (e) =>{
    e.preventDefault()
    setError(null)
    try{
      const res = await api.post('/auth/signup', { name, email, password })
      localStorage.setItem('fin_token', res.token)
      nav('/dashboard')
    }catch(err){
      setError(err?.message || 'Signup failed')
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-2xl font-semibold mb-4">Create account</h2>
      {error && <div className="text-red-600 mb-3">{error}</div>}
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm">Name</label>
          <input className="w-full border p-2 rounded" value={name} onChange={e=>setName(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm">Email</label>
          <input className="w-full border p-2 rounded" value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm">Password</label>
          <input type="password" className="w-full border p-2 rounded" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <div className="flex items-center justify-end">
          <button className="bg-indigo-600 text-white px-4 py-2 rounded">Create account</button>
        </div>
      </form>
    </div>
  )
}
