export const env = {
  apiBaseUrl:
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000",
  appName: process.env.NEXT_PUBLIC_APP_NAME ?? "UI Stock Agent",
  enableMocks: process.env.NEXT_PUBLIC_ENABLE_MOCKS === "true",
} as const;
