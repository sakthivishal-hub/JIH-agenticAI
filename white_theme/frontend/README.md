# SignalHire

SignalHire is a React-powered live job discovery interface. It combines JSearch (via RapidAPI) with public job feeds from Remotive, RemoteOK, and Arbeitnow. API credentials stay server-side and are never sent to the browser.

## Run locally

1. Copy `.env.example` to `.env`.
2. Put your RapidAPI JSearch key in `JSEARCH_API_KEY`.
3. Run `node server.js`.
4. Open `http://127.0.0.1:5173`.

The login and sign-up screen is a UI demo that stores no account data. Use a real authentication service such as Clerk, Auth0, or Supabase Auth before production.