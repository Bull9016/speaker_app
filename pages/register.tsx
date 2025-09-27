import { useState } from 'react'
import { saveSpeaker } from '../lib/speakerStorage'

export default function RegisterPage() {
  const [form, setForm] = useState<any>({ full_name: '', email: '', mobile: '', food_choice: 'Veg' })
  const [loading, setLoading] = useState(false)

  function update(k: string, v: any) { setForm((f: any) => ({ ...f, [k]: v })) }

  async function handleSubmit(e: any) {
    e.preventDefault()
    // basic validation
    if (!form.full_name || !form.email || !form.mobile) return alert('Full name, email and mobile are required')
    setLoading(true)
    const res = await saveSpeaker(form)
    setLoading(false)
    if (res.error) alert('Save error: ' + JSON.stringify(res.error))
    else {
      alert('Registered!')
      setForm({ full_name: '', email: '', mobile: '', food_choice: 'Veg' })
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h2 className="text-2xl mb-4">Speaker Registration</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-3">
        <input className="p-2 border" placeholder="Full name*" value={form.full_name} onChange={(e) => update('full_name', e.target.value)} />
        <input className="p-2 border" placeholder="Email*" value={form.email} onChange={(e) => update('email', e.target.value)} />
        <input className="p-2 border" placeholder="Mobile*" value={form.mobile} onChange={(e) => update('mobile', e.target.value)} />
        <select className="p-2 border" value={form.track || ''} onChange={(e) => update('track', e.target.value)}>
          <option value="">Select track</option>
          <option>Track 1</option>
          <option>Track 2</option>
        </select>
        <select className="p-2 border" value={form.session_category || ''} onChange={(e) => update('session_category', e.target.value)}>
          <option value="">Session category</option>
          <option>Master Class</option>
          <option>Demo Pod</option>
          <option>Talk</option>
        </select>
        <select className="p-2 border" value={form.tshirt_size || ''} onChange={(e) => update('tshirt_size', e.target.value)}>
          <option value="">T-shirt size</option>
          <option>S</option>
          <option>M</option>
          <option>L</option>
          <option>XL</option>
        </select>
        <input className="p-2 border" placeholder="Speaker 2 name" value={form.speaker2_name || ''} onChange={(e) => update('speaker2_name', e.target.value)} />
        <input className="p-2 border" placeholder="Speaker 2 email" value={form.speaker2_email || ''} onChange={(e) => update('speaker2_email', e.target.value)} />
        <select className="p-2 border" value={form.speaker2_tshirt || ''} onChange={(e) => update('speaker2_tshirt', e.target.value)}>
          <option value="">Speaker 2 T-shirt size</option>
          <option>S</option>
          <option>M</option>
          <option>L</option>
          <option>XL</option>
        </select>
        <select className="p-2 border" value={form.food_choice} onChange={(e) => update('food_choice', e.target.value)}>
          <option>Veg</option>
          <option>Non-Veg</option>
        </select>
        <input className="p-2 border" placeholder="Blood group" value={form.blood_group || ''} onChange={(e) => update('blood_group', e.target.value)} />
        <input className="p-2 border" placeholder="Emergency contact name" value={form.emergency_contact_name || ''} onChange={(e) => update('emergency_contact_name', e.target.value)} />
        <input className="p-2 border" placeholder="Emergency contact number" value={form.emergency_contact_number || ''} onChange={(e) => update('emergency_contact_number', e.target.value)} />
        <input className="p-2 border" placeholder="LinkedIn profile URL" value={form.linkedin || ''} onChange={(e) => update('linkedin', e.target.value)} />
        <input className="p-2 border" placeholder="SAP Community URL" value={form.sap_community || ''} onChange={(e) => update('sap_community', e.target.value)} />
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-indigo-600 text-white rounded" type="submit" disabled={loading}>Register</button>
        </div>
      </form>
    </div>
  )
}
