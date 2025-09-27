import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabaseClient'

export default function Dashboard() {
  const [sessions, setSessions] = useState<any[]>([])

  useEffect(() => {
    async function load() {
      const { data } = await supabase.from('sessions').select('*').order('created_at', { ascending: false })
      setSessions(data || [])
    }
    load()
  }, [])

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h2 className="text-2xl mb-4">Speaker Dashboard</h2>
      <a href="/session/new" className="px-3 py-2 bg-blue-600 text-white rounded">Submit session</a>
      <div className="mt-6">
        <h3 className="text-xl">My sessions</h3>
        <ul>
          {sessions.map((s) => (
            <li key={s.id} className="border p-2 my-2">
              <a href={`/session/${s.id}`} className="font-semibold">{s.title}</a>
              <div className="text-sm">Status: {s.status}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
