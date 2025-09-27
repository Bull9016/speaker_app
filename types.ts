export interface Session {
  id: string
  title: string
  abstract: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
}
