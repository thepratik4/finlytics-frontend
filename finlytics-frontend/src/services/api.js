const BASE = '' // when proxied by vite, relative paths are fine

function token(){
  return localStorage.getItem('fin_token')
}

export function getToken(){ return token() }
export function clearToken(){ localStorage.removeItem('fin_token') }

function handleRes(r){
  if(r.status === 204) return null
  return r.json().then(j=>{
    if(!r.ok){
      const err = new Error(j?.error || j?.message || 'API error')
      throw err
    }
    return j
  }).catch(()=>{
    if(!r.ok) throw new Error('API error')
    return null
  })
}

async function get(path){
  const res = await fetch(BASE + '/api' + path, {
    headers: { 'Authorization': token() ? `Bearer ${token()}` : '' }
  })
  return handleRes(res)
}

async function post(path, body){
  const res = await fetch(BASE + '/api' + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': token() ? `Bearer ${token()}` : '' },
    body: JSON.stringify(body)
  })
  return handleRes(res)
}

async function postForm(path, formData){
  const res = await fetch(BASE + '/api' + path, {
    method: 'POST',
    headers: { 'Authorization': token() ? `Bearer ${token()}` : '' },
    body: formData
  })
  return handleRes(res)
}

export default { get, post, postForm }
