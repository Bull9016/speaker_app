import { useState } from 'react'

export default function FAQPage() {
  const [q, setQ] = useState('')
  const [ans, setAns] = useState('')
  const [top, setTop] = useState<any[]>([])

  async function seed() {
    const r = await fetch('/api/faqs/seed', { method: 'POST' })
    const j = await r.json()
    alert('Seed: ' + JSON.stringify(j))
  }

  async function ask() {
    const r = await fetch('/api/faqs/query', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ q }) })
    const j = await r.json()
    setAns(j.answer || j.error)
    setTop(j.top || [])
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl mb-4">Semantic FAQ (embeddings)</h2>
      <div className="flex gap-2 mb-4">
        <button onClick={seed} className="px-3 py-1 bg-gray-700 text-white rounded">Seed sample FAQs</button>
      </div>
      <textarea value={q} onChange={(e)=>setQ(e.target.value)} className="w-full p-2 mb-2 border" placeholder="Ask a question to the FAQ bot" />
      <div className="flex gap-2 mb-4">
        <button onClick={ask} className="px-3 py-1 bg-indigo-600 text-white rounded">Ask</button>
      </div>
      {ans && <div className="p-3 bg-gray-100 mb-4">{ans}</div>}
      {top.length>0 && (
        <div>
          <h4 className="font-semibold mb-2">Top matches</h4>
          <ul>
            {top.map((t,i)=> (
              <li key={i} className="border p-2 mb-1">
                <div className="font-semibold">{t.q}</div>
                <div className="text-sm">{t.a}</div>
                <div className="text-xs text-gray-500">score: {t.score.toFixed(3)}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
