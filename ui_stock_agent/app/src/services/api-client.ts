import { env } from "@/lib/env";

type ApiRequestInit = Omit<RequestInit, "body"> & {
  body?: unknown;
};

export async function apiClient<T>(path: string, init?: ApiRequestInit): Promise<T> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    body: init?.body ? JSON.stringify(init.body) : undefined,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;

    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      // Ignore JSON parsing failures and keep the fallback message.
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}
