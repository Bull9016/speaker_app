import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { SessionContextProvider } from '@supabase/supabase-js'
import { supabase } from '../lib/supabaseClient'

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <Component {...pageProps} />
  )
}

export default MyApp
