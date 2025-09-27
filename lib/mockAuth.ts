// Simple mock auth that persists users in localStorage and exposes
// an API compatible with the small subset of Supabase auth used in the app.

type User = { email: string; password: string }

const STORAGE_KEY = 'vibestage_mock_users'
const SESS_KEY = 'vibestage_mock_session'

function loadUsers(): User[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    return JSON.parse(raw)
  } catch (e) {
    return []
  }
}

function saveUsers(users: User[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users))
}

export const mockAuth = {
  async signUp({ email, password }: { email: string; password: string }) {
    const users = loadUsers()
    if (users.find((u) => u.email === email)) {
      return { data: null, error: { message: 'User already exists' } }
    }
    users.push({ email, password })
    saveUsers(users)
    // create a session
    localStorage.setItem(SESS_KEY, JSON.stringify({ email }))
    return { data: { user: { email } }, error: null }
  },

  async signInWithPassword({ email, password }: { email: string; password: string }) {
    const users = loadUsers()
    const found = users.find((u) => u.email === email && u.password === password)
    if (!found) return { data: null, error: { message: 'Invalid credentials' } }
    localStorage.setItem(SESS_KEY, JSON.stringify({ email }))
    return { data: { user: { email } }, error: null }
  },

  async signOut() {
    localStorage.removeItem(SESS_KEY)
    return { error: null }
  },

  getSession() {
    try {
      const raw = localStorage.getItem(SESS_KEY)
      if (!raw) return null
      return JSON.parse(raw)
    } catch (e) {
      return null
    }
  }
}
