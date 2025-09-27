import dynamic from 'next/dynamic'
import { useEffect, useRef, useState } from 'react'

// html5-qrcode depends on browser APIs - import dynamically to avoid SSR issues
const Html5QrcodeScanner = dynamic(
  // @ts-ignore - dynamic import
  async () => {
    const mod = await import('html5-qrcode')
    return mod.Html5Qrcode
  },
  { ssr: false }
)

export default function ScanPage() {
  const [message, setMessage] = useState<string | null>(null)
  const [scanning, setScanning] = useState(false)
  const scannerRef = useRef<any>(null)
  const qrRegionId = 'qr-reader'

  useEffect(() => {
    // Only run in browser
    if (typeof window === 'undefined') return
    let html5QrCode: any | null = null

    async function startScanner() {
      try {
        const { Html5Qrcode } = await import('html5-qrcode')
        html5QrCode = new Html5Qrcode(qrRegionId, { verbose: false })
        scannerRef.current = html5QrCode

        // Choose back camera if available
        const devices = await Html5Qrcode.getCameras()
        const backCamera = devices.find((d: any) => /back|rear|environment/gi.test(d.label))
        const cameraId = backCamera ? backCamera.id : devices[0]?.id
        if (!cameraId) {
          setMessage('No camera found on this device')
          return
        }

        await html5QrCode.start(
          cameraId,
          {
            fps: 10,
            qrbox: { width: 300, height: 300 },
            aspectRatio: 1.0
          },
          (decodedText: string) => onScanned(decodedText),
          (errorMessage: string) => {
            // ignore transient decode errors
          }
        )
        setScanning(true)
      } catch (err: any) {
        console.error('Scanner start failed', err)
        setMessage('Failed to start camera scanner: ' + (err?.message || String(err)))
      }
    }

    startScanner()

    return () => {
      if (scannerRef.current) {
        scannerRef.current
          .stop()
          .then(() => scannerRef.current.clear())
          .catch(() => {})
      }
    }
  }, [])

  async function onScanned(token: string) {
    if (!token) return
    setMessage('Scanned token, verifying...')
    try {
      const res = await fetch('/api/qr/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      })
      const body = await res.json()
      if (!res.ok) {
        setMessage(body?.message || body?.error || 'Verification failed')
      } else {
        setMessage(`Success: ${body.message} (purpose: ${body.purpose || 'n/a'})`)
        // stop scanning on success for single-use flows
        if (scannerRef.current) {
          try {
            await scannerRef.current.stop()
            await scannerRef.current.clear()
          } catch (e) {}
          setScanning(false)
        }
      }
    } catch (err: any) {
      setMessage('Network error: ' + (err?.message || String(err)))
    }
  }

  async function handleManualSubmit(e: any) {
    e.preventDefault()
    const token = e.target.elements.token?.value
    if (!token) return setMessage('Please paste a token')
    await onScanned(token.trim())
  }

  async function resumeScanner() {
    if (scanning) return
    try {
      const { Html5Qrcode } = await import('html5-qrcode')
      const devices = await Html5Qrcode.getCameras()
      const backCamera = devices.find((d: any) => /back|rear|environment/gi.test(d.label))
      const cameraId = backCamera ? backCamera.id : devices[0]?.id
      if (!cameraId) return setMessage('No camera available')
      const html5QrCode = new Html5Qrcode(qrRegionId)
      scannerRef.current = html5QrCode
      await html5QrCode.start(cameraId, { fps: 10, qrbox: 300 }, (decoded: string) => onScanned(decoded))
      setScanning(true)
      setMessage(null)
    } catch (err: any) {
      setMessage('Failed to resume scanner: ' + (err?.message || String(err)))
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-4">
      <h1 className="text-2xl font-semibold mb-4">Live QR Scanner</h1>
      <div className="w-full max-w-lg">
        <div id={qrRegionId} className="w-full rounded overflow-hidden bg-black" style={{ height: 360 }} />
        <div className="mt-3 flex gap-2">
          <button
            onClick={async () => {
              if (scannerRef.current && scanning) {
                try {
                  await scannerRef.current.stop()
                  await scannerRef.current.clear()
                } catch (e) {}
                setScanning(false)
                setMessage('Scanner stopped')
              } else {
                resumeScanner()
              }
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded"
          >
            {scanning ? 'Stop' : 'Start'}
          </button>
          <a className="px-4 py-2 bg-gray-200 rounded" href="/checkin">Manual check-in page</a>
        </div>

        <form onSubmit={handleManualSubmit} className="mt-4">
          <label className="block text-sm font-medium text-gray-700">Paste token manually</label>
          <div className="flex gap-2 mt-1">
            <input name="token" className="flex-1 p-2 border rounded" placeholder="paste token here" />
            <button className="px-3 py-2 bg-green-600 text-white rounded">Verify</button>
          </div>
        </form>

        <div className="mt-4 p-3 bg-white rounded shadow-sm">
          <strong>Result:</strong>
          <div className="mt-2 text-sm text-gray-700">{message ?? 'Waiting for scan...'}</div>
        </div>
      </div>
    </div>
  )
}
