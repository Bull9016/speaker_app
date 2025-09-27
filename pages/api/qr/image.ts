import type { NextApiRequest, NextApiResponse } from 'next'
import QRCode from 'qrcode'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { token } = req.query
  if (!token || typeof token !== 'string') return res.status(400).json({ error: 'token required' })
  try {
    const dataUrl = await QRCode.toDataURL(token)
    return res.status(200).json({ dataUrl })
  } catch (err: any) {
    return res.status(500).json({ error: err.message })
  }
}
