import fs from 'fs'
import path from 'path'

const OPENAI_EMBED_URL = 'https://api.openai.com/v1/embeddings'

function getKey() {
  return process.env.OPENAI_API_KEY || ''
}

export async function getEmbedding(text: string): Promise<number[]> {
  const key = getKey()
  if (!key) throw new Error('OPENAI_API_KEY not set')
  const res = await fetch(OPENAI_EMBED_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${key}`,
    },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
  })
  const j = await res.json()
  if (j?.data?.[0]?.embedding) return j.data[0].embedding
  throw new Error('Failed to get embedding: ' + JSON.stringify(j))
}

export const FAQ_PATH = path.join(process.cwd(), 'data', 'faqs.json')

export async function readFaqs(): Promise<any[]> {
  try {
    const raw = await fs.promises.readFile(FAQ_PATH, 'utf8')
    return JSON.parse(raw)
  } catch (e) {
    return []
  }
}

export async function writeFaqs(list: any[]) {
  const dir = path.dirname(FAQ_PATH)
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
  await fs.promises.writeFile(FAQ_PATH, JSON.stringify(list, null, 2), 'utf8')
}
