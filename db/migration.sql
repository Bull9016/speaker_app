-- Supabase / Postgres migration for VibeStage scaffold
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  role text DEFAULT 'speaker',
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  abstract text,
  status text DEFAULT 'pending',
  created_at timestamptz DEFAULT now()
);

-- QR tokens are per-session and optionally per-speaker. They support purposes (checkin, tshirt, attendance), expiration and single-use behavior.
CREATE TABLE IF NOT EXISTS qr_tokens (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES sessions(id) ON DELETE CASCADE,
  speaker_id uuid REFERENCES users(id) ON DELETE SET NULL,
  token text UNIQUE NOT NULL,
  purpose text DEFAULT 'checkin',
  single_use boolean DEFAULT true,
  metadata jsonb,
  expires_at timestamptz,
  used boolean DEFAULT false,
  used_at timestamptz,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES sessions(id) ON DELETE CASCADE,
  filename text,
  url text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES sessions(id) ON DELETE CASCADE,
  rating int,
  comments text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS certificates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES sessions(id) ON DELETE CASCADE,
  url text,
  published_at timestamptz
);
