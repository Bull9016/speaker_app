import { supabase, SUPABASE_CONFIGURED } from './supabaseClient'

type Speaker = {
  full_name: string
  email: string
  mobile: string
  track?: string
  session_category?: string
  tshirt_size?: string
  speaker2_name?: string
  speaker2_email?: string
  speaker2_tshirt?: string
  food_choice?: string
  blood_group?: string
  emergency_contact_name?: string
  emergency_contact_number?: string
  linkedin?: string
  sap_community?: string
}

const MOCK_KEY = 'vibestage_mock_speakers'

function mockSave(s: Speaker) {
  const raw = localStorage.getItem(MOCK_KEY)
  const arr = raw ? JSON.parse(raw) : []
  arr.push({ ...s, id: Date.now().toString() })
  localStorage.setItem(MOCK_KEY, JSON.stringify(arr))
  return { data: { id: arr[arr.length - 1].id }, error: null }
}

export async function saveSpeaker(s: Speaker) {
  if (!SUPABASE_CONFIGURED) {
    return mockSave(s)
  }
  // attempt insert into users table
  const { data, error } = await supabase.from('users').insert([{ email: s.email }]).select()
  if (error) return { data: null, error }
  // optionally insert a sessions row if you want, but for registration we keep to users
  return { data, error }
}

export async function getMockSpeakers() {
  const raw = localStorage.getItem(MOCK_KEY)
  return raw ? JSON.parse(raw) : []
}
