import { GoogleGenerativeAI } from '@google/generative-ai'

function getKey() {
  return process.env.GEMINI_API_KEY || ''
}

const genAI = new GoogleGenerativeAI(getKey())

export async function aiChat(prompt: string) {
  const key = getKey()
  if (!key) throw new Error('GEMINI_API_KEY not set')
  const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' })
  const result = await model.generateContent(prompt)
  return result.response.text()
}

export async function aiDraftEmail({ sessionTitle, speakerName, decision, tone }: { sessionTitle: string, speakerName?: string, decision: 'approved'|'rejected'|'hold', tone?: string }) {
  const key = getKey()
  if (!key) throw new Error('GEMINI_API_KEY not set')
  const decisionText = decision === 'approved' ? 'approved' : decision === 'rejected' ? 'rejected' : 'on hold'
  const prompt = `Write a ${tone || 'professional and friendly'} email to ${speakerName || 'the speaker'} informing them that their session titled "${sessionTitle}" has been ${decisionText}. Include next steps and contact info.`
  return aiChat(prompt)
}

export async function aiOptimizeAgenda(sessions: Array<{ id: string, title: string, topic?: string, speaker?: string, availability?: string[] }>, constraints?: string) {
  const key = getKey()
  if (!key) throw new Error('GEMINI_API_KEY not set')
  const prompt = `You are an events optimizer. Given the following sessions in JSON: ${JSON.stringify(sessions)} and constraints: ${constraints || 'none'}, produce a suggested schedule mapping session id to timeslot (e.g., 2025-09-30T10:00) and room. Output JSON array [{id, start, end, room}].`
  const out = await aiChat(prompt)
  // Try to parse JSON; if parsing fails, return raw text
  try {
    const parsed = JSON.parse(out)
    return parsed
  } catch (e) {
    return { text: out }
  }
}
