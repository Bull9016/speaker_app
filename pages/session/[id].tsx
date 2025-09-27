import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'
import { supabase } from '../../lib/supabaseClient'

export default function SessionDetail() {
  const router = useRouter()
  const { id } = router.query
  const [session, setSession] = useState<any | null>(null)

  useEffect(() => {
    if (!id) return
    async function load() {
      const { data } = await supabase.from('sessions').select('*').eq('id', id).single()
      setSession(data)
    }
    load()
  }, [id])

  const [speakers, setSpeakers] = useState<any[]>([])
  const [selectedSpeaker, setSelectedSpeaker] = useState<string | null>(null)
  const [purpose, setPurpose] = useState('checkin')
  const [expiresMinutes, setExpiresMinutes] = useState<number | ''>(30)
  const [singleUse, setSingleUse] = useState(true)
  const [qrDataUrl, setQrDataUrl] = useState<string | null>(null)

  useEffect(() => {
    async function loadSpeakers() {
      const { data } = await supabase.from('users').select('*').eq('role', 'speaker')
      setSpeakers(data || [])
      if (data && data.length > 0) setSelectedSpeaker(data[0].id)
    }
    loadSpeakers()
  }, [])

  async function generateQR() {
    const body: any = { session_id: id, purpose, single_use: singleUse }
    if (selectedSpeaker) body.speaker_id = selectedSpeaker
    if (expiresMinutes) body.expires_in_minutes = expiresMinutes
    const res = await fetch('/api/qr/generate', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) })
    const j = await res.json()
    if (j?.token) {
      const imgRes = await fetch('/api/qr/image?token=' + encodeURIComponent(j.token))
      const imgJson = await imgRes.json()
      setQrDataUrl(imgJson.dataUrl)
    } else if (j?.error) {
      alert('Error: ' + j.error)
    }
  }

  if (!session) return <div className="p-6">Loading...</div>

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h2 className="text-xl">{session.title}</h2>
      <p className="my-4">{session.abstract}</p>
      <div>Status: {session.status}</div>
      {session.status === 'approved' && (
        <div className="mt-4">
          <div className="mb-2">
            <label className="mr-2">Speaker:</label>
            <select value={selectedSpeaker || ''} onChange={(e) => setSelectedSpeaker(e.target.value)}>
              {speakers.map(s => <option key={s.id} value={s.id}>{s.email}</option>)}
            </select>
          </div>
          <div className="mb-2">
            <label className="mr-2">Purpose:</label>
            <select value={purpose} onChange={(e) => setPurpose(e.target.value)}>
              <option value="checkin">Check-in</option>
              <option value="tshirt">T-shirt pickup</option>
              <option value="attendance">Session attendance</option>
            </select>
          </div>
          <div className="mb-2">
            <label className="mr-2">Expires (minutes):</label>
            <input type="number" value={String(expiresMinutes)} onChange={(e) => setExpiresMinutes(e.target.value ? Number(e.target.value) : '')} className="w-24" />
          </div>
          <div className="mb-2">
            <label className="mr-2">Single use:</label>
            <input type="checkbox" checked={singleUse} onChange={(e) => setSingleUse(e.target.checked)} />
          </div>
          <button onClick={generateQR} className="px-3 py-2 bg-yellow-600 text-white rounded">Generate QR</button>
          {qrDataUrl && <div className="mt-4"><img src={qrDataUrl} alt="QR" /></div>}
        </div>
      )}
    </div>
  )
}
