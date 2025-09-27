import type { NextApiRequest, NextApiResponse } from 'next'
import { supabaseAdmin } from '../../../../lib/supabaseServer'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { id } = req.query
  try {
    const { error } = await supabaseAdmin.from('sessions').update({ status: 'approved' }).eq('id', id)
    if (error) return res.status(500).json({ error: error.message })
    return res.status(200).json({ ok: true })
  } catch (err: any) {
    return res.status(500).json({ error: err.message })
  }
}
