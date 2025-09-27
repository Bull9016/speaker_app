declare module 'html5-qrcode' {
  export class Html5Qrcode {
    constructor(elementId: string | HTMLElement, config?: any)
    static getCameras(): Promise<Array<{ id: string; label: string }>>
    start(cameraIdOrDeviceId: string, config?: any, qrCodeSuccessCallback?: (decodedText: string) => void, qrCodeErrorCallback?: (errorMessage: string) => void): Promise<void>
    stop(): Promise<void>
    clear(): Promise<void>
  }
  export default Html5Qrcode
}
