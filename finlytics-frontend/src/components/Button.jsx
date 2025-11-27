import React from 'react'

export default function Button({ children, className='', ...props }){
  return (
    <button className={`inline-flex items-center px-3 py-1 rounded bg-indigo-600 text-white ${className}`} {...props}>{children}</button>
  )
}
