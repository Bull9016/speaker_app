# VibeStage — Next.js + Supabase Scaffold

This is a hackathon-ready scaffold for a Speaker/Event management app. It includes basic auth via Supabase, session submission, manager approval, QR token generation and a QR check-in page.

Quick start
1. Create a Supabase project and get the URL and anon key (and service role key if you plan to run server-side seeds).
2. Copy `.env.local.example` to `.env.local` and fill values for NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.
3. Install deps:

```powershell
cd speaker_app
npm install
```

4. Run dev server:

```powershell
npm run dev
```

5. Run seed (after setting service role key):

```powershell
npm run seed
```

Notes
- This scaffold uses the pages router and Next.js API routes. Fill in production-grade auth checks before deploying.
- See `db/migration.sql` for the schema to create in Supabase (SQL editor).

Supabase setup
1. In your Supabase project, open the SQL editor and run the statements in `db/migration.sql` to create the tables.
2. In the project Settings → API, copy the Project URL and anon key into `.env.local` as `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
3. (Optional) To run server-side seeds or admin tasks, add `SUPABASE_SERVICE_ROLE_KEY` to `.env.local` (this is secret — do NOT commit it).

If you don't have Supabase keys handy, the app will run in mock mode (localStorage) for auth and speaker registration. Use the demo seed on `/auth` to create a demo account.

## Streamlit App (Speaker Management)

The Streamlit app provides a full speaker management system with user registration, session submission, event management, and more.

### Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Initialize the database:

```bash
python init_db.py
```

3. Run the app:

```bash
streamlit run app.py
```

### Demo Credentials

For testing the custom login:

- **Event Manager**: Email: manager@test.com, Password: test123
- **Speaker**: Email: speaker@test.com, Password: test123

### Deployment

The app uses SQLite by default. For production, set the `DATABASE_URL` environment variable to a PostgreSQL connection string to use Postgres instead.

The app binds to `0.0.0.0` and uses the `PORT` environment variable for the server port (defaults to 8501).
