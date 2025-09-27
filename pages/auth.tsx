import { useState } from 'react'
import { supabase, SUPABASE_CONFIGURED } from '../lib/supabaseClient'
import { mockAuth } from '../lib/mockAuth'

export default function AuthPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSignUp() {
    setLoading(true)
    const client = SUPABASE_CONFIGURED ? supabase.auth : mockAuth
    const res = await client.signUp({ email, password })
    setLoading(false)
    if (res.error) alert(res.error.message)
    else alert('Signed up (check email if using real Supabase)')
  }

  async function handleSignIn() {
    setLoading(true)
    const client = SUPABASE_CONFIGURED ? supabase.auth : mockAuth
    const res = await client.signInWithPassword({ email, password })
    setLoading(false)
    if (res.error) alert(res.error.message)
    else alert('Signed in')
  }

  function demoSeed() {
    // create a demo account into mock storage (only for mock mode)
    if (SUPABASE_CONFIGURED) return alert('Dev/demo seed only available in mock mode')
    localStorage.setItem('vibestage_mock_users', JSON.stringify([{ email: 'speaker@demo.com', password: 'password' }]))
    alert('Demo user created: speaker@demo.com / password')
  }

  function showSession() {
    if (SUPABASE_CONFIGURED) return alert('Only for mock mode')
    const sess = mockAuth.getSession()
    alert('Current mock session: ' + JSON.stringify(sess))
  }

  return (
    <div className="max-w-md mx-auto p-6">
      <h2 className="text-2xl mb-4">Login / Register</h2>
      <input className="w-full p-2 mb-2 border" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input type="password" className="w-full p-2 mb-2 border" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <div className="flex gap-2">
        <button onClick={handleSignIn} className="px-4 py-2 bg-blue-600 text-white rounded" disabled={loading}>Sign in</button>
        <button onClick={handleSignUp} className="px-4 py-2 bg-green-600 text-white rounded" disabled={loading}>Sign up</button>
      </div>
    </div>
  )
}
