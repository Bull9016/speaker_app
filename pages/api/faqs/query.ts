import type { NextApiRequest, NextApiResponse } from 'next'
import { getEmbedding, readFaqs } from '../../../lib/embeddings'
import { aiChat } from '../../../lib/ai'

function cosine(a: number[], b: number[]) {
  let dot = 0, na = 0, nb = 0
  for (let i = 0; i < a.length; i++) { dot += a[i]*b[i]; na += a[i]*a[i]; nb += b[i]*b[i] }
  return dot / (Math.sqrt(na) * Math.sqrt(nb) + 1e-10)
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { q } = req.body
  if (!q) return res.status(400).json({ error: 'q required' })
  try {
    const emb = await getEmbedding(q)
    const faqs = await readFaqs()
    const scored = faqs.map((f: any) => ({ ...f, score: cosine(emb, f.embedding) }))
    scored.sort((a: any,b: any) => b.score - a.score)
    const top = scored.slice(0, 3)
    const context = top.map((t: any, i: number) => `FAQ ${i+1}: Q: ${t.q} A: ${t.a}`).join('\n')
    const prompt = `You are an assistant answering user question using only the context below when possible. Context:\n${context}\nUser question: ${q}\nAnswer concisely and point to the FAQ number when appropriate.`
    const answer = await aiChat(prompt)
    return res.status(200).json({ answer, top })
  } catch (err: any) {
    return res.status(500).json({ error: err.message })
  }
}
