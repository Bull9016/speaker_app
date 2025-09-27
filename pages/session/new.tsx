import { useState } from 'react'
import { supabase } from '../../lib/supabaseClient'

export default function NewSession() {
  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')

  async function submit() {
    const { data, error } = await supabase.from('sessions').insert([{ title, abstract, status: 'pending' }])
    if (error) alert(error.message)
    else {
      alert('Submitted')
      setTitle('')
      setAbstract('')
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-xl mb-4">Submit a session</h2>
      <input value={title} onChange={(e) => setTitle(e.target.value)} className="w-full p-2 mb-2 border" placeholder="Talk title" />
      <textarea value={abstract} onChange={(e) => setAbstract(e.target.value)} className="w-full p-2 mb-2 border" placeholder="Abstract" />
      <button onClick={submit} className="px-4 py-2 bg-blue-600 text-white rounded">Submit</button>
    </div>
  )
}
