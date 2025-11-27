import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import Session from './pages/Session'
import Analysis from './pages/Analysis'
import Header from './components/Header'
import { getToken } from './services/api'

function PrivateRoute({ children }){
  const token = getToken()
  if(!token) return <Navigate to="/login" replace />
  return children
}

export default function App(){
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <main className="p-4 max-w-6xl mx-auto">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<Login/>} />
          <Route path="/signup" element={<Signup/>} />
          <Route path="/dashboard" element={<PrivateRoute><Dashboard/></PrivateRoute>} />
          <Route path="/session/:id" element={<PrivateRoute><Session/></PrivateRoute>} />
          <Route path="/analysis" element={<PrivateRoute><Analysis/></PrivateRoute>} />
        </Routes>
      </main>
    </div>
  )
}
