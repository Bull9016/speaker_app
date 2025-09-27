import Link from 'next/link'

export default function Home() {
  return (
    <div className="max-w-3xl mx-auto p-8">
      <h1 className="text-4xl font-bold mb-4">VibeStage — Speaker Manager</h1>
      <p className="mb-6">Demo-ready scaffold: register as a speaker, submit sessions, manager approves, QR check-in.</p>
      <div className="flex gap-4">
        <Link href="/auth" className="px-4 py-2 bg-blue-600 text-white rounded">Login / Register</Link>
        <Link href="/dashboard" className="px-4 py-2 bg-green-600 text-white rounded">Speaker Dashboard</Link>
        <Link href="/manager" className="px-4 py-2 bg-gray-700 text-white rounded">Manager Dashboard</Link>
        <Link href="/checkin" className="px-4 py-2 bg-yellow-600 text-white rounded">QR Check-in</Link>
      </div>
    </div>
  )
}
