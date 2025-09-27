import type { NextApiRequest, NextApiResponse } from 'next'
import { sendEmail } from '../../../lib/sendgrid'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { to, subject, text, html } = req.body
  if (!to || !subject) return res.status(400).json({ error: 'to and subject required' })
  try {
    const r = await sendEmail({ to, subject, text, html })
    return res.status(200).json({ ok: true, result: r })
  } catch (err: any) {
    return res.status(500).json({ error: err.message })
  }
}
