import type { NextApiRequest, NextApiResponse } from 'next'
import { supabaseAdmin } from '../../../lib/supabaseServer'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { token } = req.body
  if (!token) return res.status(400).json({ error: 'token required' })
  try {
    const { data } = await supabaseAdmin.from('qr_tokens').select('*').eq('token', token).single()
    if (!data) return res.status(404).json({ message: 'Token not found' })
    // Check expiration
    if (data.expires_at) {
      const exp = new Date(data.expires_at)
      if (exp.getTime() < Date.now()) return res.status(400).json({ message: 'Token expired' })
    }
    if (data.single_use && data.used) return res.status(400).json({ message: 'Token already used' })
    if (data.single_use) {
      const { error } = await supabaseAdmin.from('qr_tokens').update({ used: true, used_at: new Date() }).eq('token', token)
      if (error) return res.status(500).json({ error: error.message })
    }
    return res.status(200).json({ message: 'Check-in successful', session_id: data.session_id, purpose: data.purpose, speaker_id: data.speaker_id })
  } catch (err: any) {
    return res.status(500).json({ error: err.message })
  }
}
