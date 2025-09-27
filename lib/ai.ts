const OPENAI_URL = 'https://api.openai.com/v1/chat/completions'

function getKey() {
  return process.env.OPENAI_API_KEY || ''
}

export async function aiChat(prompt: string) {
  const key = getKey()
  if (!key) throw new Error('OPENAI_API_KEY not set')
  const res = await fetch(OPENAI_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${key}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 600,
    }),
  })
  const j = await res.json()
  return j?.choices?.[0]?.message?.content || ''
}

export async function aiDraftEmail({ sessionTitle, speakerName, decision, tone }: { sessionTitle: string, speakerName?: string, decision: 'approved'|'rejected'|'hold', tone?: string }) {
  const key = getKey()
  if (!key) throw new Error('OPENAI_API_KEY not set')
  const decisionText = decision === 'approved' ? 'approved' : decision === 'rejected' ? 'rejected' : 'on hold'
  const prompt = `Write a ${tone || 'professional and friendly'} email to ${speakerName || 'the speaker'} informing them that their session titled "${sessionTitle}" has been ${decisionText}. Include next steps and contact info.`
  return aiChat(prompt)
}

export async function aiOptimizeAgenda(sessions: Array<{ id: string, title: string, topic?: string, speaker?: string, availability?: string[] }>, constraints?: string) {
  const key = getKey()
  if (!key) throw new Error('OPENAI_API_KEY not set')
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
