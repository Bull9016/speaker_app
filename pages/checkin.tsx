import { useState } from 'react'

export default function Checkin() {
  const [token, setToken] = useState('')
  const [result, setResult] = useState<string | null>(null)

  async function verify() {
    const res = await fetch('/api/qr/verify', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ token }) })
    const j = await res.json()
    if (j?.error) setResult('Error: ' + j.error)
    else if (j?.message) setResult(`${j.message} (purpose: ${j.purpose || 'n/a'})\nSession: ${j.session_id || 'n/a'}\nSpeaker: ${j.speaker_id || 'n/a'}`)
    else setResult('No response')
  }

  return (
    <div className="max-w-md mx-auto p-6">
      <h2 className="text-xl mb-4">QR Check-in</h2>
      <input className="w-full p-2 mb-2 border" value={token} onChange={(e) => setToken(e.target.value)} placeholder="Paste QR token" />
      <button onClick={verify} className="px-4 py-2 bg-blue-600 text-white rounded">Verify</button>
      {result && <div className="mt-4 p-3 bg-gray-100">{result}</div>}
    </div>
  )
}
