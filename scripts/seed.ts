import { createClient } from '@supabase/supabase-js'

const url = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const key = process.env.SUPABASE_SERVICE_ROLE_KEY || ''

if (!url || !key) {
  console.error('Missing Supabase environment variables. Please set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env.local')
  process.exit(1)
}

const supabase = createClient(url, key)

async function seed() {
  try {
    console.log('Seeding...')
    // Use upsert (onConflict: 'email') to avoid duplicate errors if run multiple times.
    const { error: e1 } = await supabase.from('users').upsert([
      { email: 'manager@demo.com', role: 'manager' },
      { email: 'speaker@demo.com', role: 'speaker' }
    ], { onConflict: 'email' })
    if (e1) throw e1

    // Insert a demo session if it doesn't already exist (upsert by title)
    const { error: e2 } = await supabase.from('sessions').upsert([
      { title: 'Demo Talk', abstract: 'This is a demo session', status: 'pending' }
    ], { onConflict: 'title' })
    if (e2) throw e2

    console.log('Seed complete')
  } catch (err: any) {
    console.error('Seeding failed:', err.message || err)
    process.exit(1)
  }
}

seed()
