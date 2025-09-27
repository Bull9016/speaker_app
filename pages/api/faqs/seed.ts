import type { NextApiRequest, NextApiResponse } from 'next'
import { getEmbedding, writeFaqs } from '../../../lib/embeddings'

const SAMPLE_FAQS = [
  { q: 'What file formats are acceptable for slides?', a: 'PDF and PPTX are preferred. Keep file size under 20MB.' },
  { q: 'When is the submission deadline?', a: 'The submission deadline is 2 weeks before the event.' },
  { q: 'How do I request a microphone?', a: 'Use the speaker resources page and fill the AV request form.' }
]

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  try {
    const enriched = [] as any[]
    for (const f of SAMPLE_FAQS) {
      const embedding = await getEmbedding(f.q + ' ' + f.a)
      enriched.push({ ...f, embedding })
    }
    await writeFaqs(enriched)
    return res.status(200).json({ ok: true, count: enriched.length })
  } catch (err: any) {
    return res.status(500).json({ error: err.message })
  }
}
