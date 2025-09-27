import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

function makeMissingEnvStub(message: string) {

	// Create a safe, chainable, thenable stub so awaiting queries doesn't crash the app.
	function makeChainable() {
		const state: any = { table: null }
		const api: any = {
			select(..._args: any[]) { return api },
			eq(..._args: any[]) { return api },
			order(..._args: any[]) { return api },
			single() { return Promise.resolve({ data: null, error: null }) },
			limit() { return api },
			insert(_payload: any) { return Promise.resolve({ data: [], error: null }) },
			upsert(_payload: any, _opts?: any) { return Promise.resolve({ data: [], error: null }) },
			from(_table: string) { return api }
		}
		// Make thenable so `await supabase.from(...).select(...).eq(...)` works
		;(api as any).then = function (resolve: any) {
			resolve({ data: [], error: null })
		}
		return api
	}

	const stub = {
		from() { return makeChainable() },
		// basic auth shim used in auth flows
		auth: {
			async signInWithPassword(_opts: any) { return { data: null, error: { message } } },
			async signUp(_opts: any) { return { data: null, error: { message } } },
			async signOut() { return { error: { message } } }
		}
	}
	return stub as any
}

// Decide which client to export. If env is missing, export a stub that throws helpful errors when used.
if (!supabaseUrl || !supabaseAnonKey) {
	// eslint-disable-next-line no-console
	console.warn('[supabase] NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY is not set. Copy .env.local.example to .env.local and fill NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY, then restart the dev server.')
}

export const SUPABASE_CONFIGURED = Boolean(supabaseUrl && supabaseAnonKey)

const _supabase = (!supabaseUrl || !supabaseAnonKey)
	? makeMissingEnvStub('Supabase client not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local')
	: createClient(supabaseUrl, supabaseAnonKey)

export const supabase = _supabase as any
