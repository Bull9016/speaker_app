import sg from '@sendgrid/mail'

export async function sendEmail({ to, subject, text, html }: { to: string, subject: string, text?: string, html?: string }) {
  const key = process.env.SENDGRID_API_KEY || ''
  if (!key) {
    console.warn('[sendgrid] SENDGRID_API_KEY not set — simulating send')
    return { simulated: true }
  }
  sg.setApiKey(key)
  const msg: any = { to, from: process.env.SENDGRID_FROM || 'no-reply@example.com', subject }
  if (html) msg.html = html
  else msg.text = text
  const res = await sg.send(msg)
  return res
}
