import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getToken, clearToken } from '../services/api'

export default function Header(){
  const nav = useNavigate()
  const token = getToken()
  const logout = ()=>{ clearToken(); nav('/login') }

  return (
    <header className="bg-white border-b">
      <div className="max-w-6xl mx-auto p-4 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold text-indigo-600">Finlytics</Link>
        <nav>
          {token ? (
            <div className="flex gap-3 items-center">
              <Link to="/dashboard" className="text-sm text-slate-700">Dashboard</Link>
              <button onClick={logout} className="text-sm text-red-600">Logout</button>
            </div>
          ) : (
            <div className="flex gap-3">
              <Link to="/login" className="text-sm text-slate-700">Login</Link>
              <Link to="/signup" className="text-sm text-indigo-600">Sign up</Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  )
}
