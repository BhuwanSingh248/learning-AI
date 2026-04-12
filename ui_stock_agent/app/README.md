# UI Stock Agent App

Next.js frontend scaffold for the stock recommendation agent.

## Scripts

* `npm run dev` starts the app locally
* `npm run build` creates a production build
* `npm run lint` runs ESLint
* `npm run test` runs Vitest
* `npm run test:e2e` runs Playwright

## Environment

Copy `.env.example` to `.env.local` and adjust values if needed.

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_APP_NAME=UI Stock Agent
NEXT_PUBLIC_ENABLE_MOCKS=false
```

## Current Backend Contract

The existing backend currently exposes:

* `POST /suggest`
* request: `symbols`, `lookback_days`
* response: `symbol`, `score`, `decision`, `reason`

The status page uses `GET /openapi.json` as a temporary health signal until a dedicated health endpoint exists.
