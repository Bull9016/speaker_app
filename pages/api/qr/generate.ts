import type { NextApiRequest, NextApiResponse } from 'next'
import { supabaseAdmin } from '../../../lib/supabaseServer'
import crypto from 'crypto'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { session_id, speaker_id, purpose = 'checkin', expires_in_minutes, single_use = true, metadata } = req.body
  if (!session_id) return res.status(400).json({ error: 'session_id required' })
  try {
    const token = crypto.randomBytes(12).toString('hex')
    let expires_at = null
    if (expires_in_minutes) {
      expires_at = new Date(Date.now() + Number(expires_in_minutes) * 60 * 1000)
    }
    const payload: any = { session_id, token, purpose, single_use, metadata }
    if (speaker_id) payload.speaker_id = speaker_id
    if (expires_at) payload.expires_at = expires_at
    const { error, data } = await supabaseAdmin.from('qr_tokens').insert([payload]).select().single()
    if (error) return res.status(500).json({ error: error.message })
    return res.status(200).json({ token: data.token, id: data.id, expires_at: data.expires_at })
  } catch (err: any) {
    return res.status(500).json({ error: err.message })
  }
}
