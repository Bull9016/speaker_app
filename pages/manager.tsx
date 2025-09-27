import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabaseClient'

function ChatBox() {
  const [prompt, setPrompt] = useState('')
  const [answer, setAnswer] = useState('')
  async function ask() {
    const r = await fetch('/api/ai/chat', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ prompt }) })
    const j = await r.json()
    setAnswer(j.answer || j.error)
  }
  return (
    <div className="p-3 border my-3">
      <h4 className="font-semibold">AI Chat (FAQ)</h4>
      <textarea className="w-full p-2 my-2 border" value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Ask about speaker FAQs, deadlines, etc." />
      <div className="flex gap-2">
        <button onClick={ask} className="px-3 py-1 bg-indigo-600 text-white rounded">Ask AI</button>
      </div>
      {answer && <pre className="mt-3 whitespace-pre-wrap">{answer}</pre>}
    </div>
  )
}

export default function Manager() {
  const [sessions, setSessions] = useState<any[]>([])

  useEffect(() => {
    async function load() {
      const { data } = await supabase.from('sessions').select('*').eq('status', 'pending').order('created_at', { ascending: false })
      setSessions(data || [])
    }
    load()
  }, [])

  async function approve(id: string) {
    const res = await fetch('/api/sessions/' + id + '/approve', { method: 'POST' })
    if (res.ok) alert('Approved')
    else alert('Error')
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl mb-4">Manager Queue</h2>
      <ChatBox />
      <div className="p-3 border mb-4">
        <h4 className="font-semibold">AI Tools</h4>
        <div className="flex gap-2 mt-2">
          <button onClick={async () => {
            // fetch pending sessions and call optimize
            const { data } = await supabase.from('sessions').select('*').eq('status', 'pending')
            const res = await fetch('/api/ai/optimize', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ sessions: data }) })
            const j = await res.json()
            // safely stringify the plan (or the whole response) so we never call .slice on undefined
            const planStr = JSON.stringify(j?.plan ?? j ?? {})
            alert('Optimize result: ' + planStr.slice(0, 300))
          }} className="px-3 py-1 bg-purple-600 text-white rounded">Optimize Agenda</button>

          <button onClick={async () => {
            // generate an email draft for first pending session
            const { data } = await supabase.from('sessions').select('*').eq('status', 'pending').limit(1)
            if (!data || data.length === 0) return alert('No pending sessions')
            const s = data[0]
            const res = await fetch('/api/ai/email', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ sessionTitle: s.title, speakerName: s.speaker_name || 'Speaker', decision: 'approved', tone: 'friendly and excited' }) })
            const j = await res.json()
            const draft = j.draft || j.error
            if (!draft) return alert('No draft returned')
            if (confirm('Send this draft via email?\n\n' + draft.slice(0,200) + '...')) {
              // send email (demo recipient)
              const to = prompt('Recipient email (demo: speaker@demo.com)', 'speaker@demo.com')
              if (!to) return
              const sendRes = await fetch('/api/email/send', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ to, subject: `Update on your session: ${s.title}`, text: draft }) })
              const sendJson = await sendRes.json()
              if (sendJson.ok) alert('Email sent (or simulated)')
              else alert('Send error: ' + JSON.stringify(sendJson))
            } else {
              alert('Draft preview:\n' + draft)
            }
          }} className="px-3 py-1 bg-emerald-600 text-white rounded">Draft email (approve)</button>
        </div>
      </div>
      <ul>
        {sessions.map((s) => (
          <li key={s.id} className="border p-3 mb-2 flex justify-between">
            <div>
              <div className="font-semibold">{s.title}</div>
              <div className="text-sm">{s.abstract}</div>
            </div>
            <div className="flex flex-col gap-2">
              <button onClick={() => approve(s.id)} className="px-3 py-1 bg-green-600 text-white rounded">Approve</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
