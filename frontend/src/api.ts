import type { AskResponse } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "http://localhost:8000" : "");

async function request<T>(path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method: body ? "POST" : "GET",
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error(`Cannot reach the CodeMind backend at ${API_URL}. Confirm the backend is running and retry.`);
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  clone: (repoUrl: string) => request<{ status: string; repo_id: string }>("/clone", { repo_url: repoUrl }),
  index: (repoId: string) =>
    request<{ status: string; files: number; chunks: number }>("/index", { repo_id: repoId }),
  ask: (repoId: string, question: string) =>
    request<AskResponse>("/ask", { repo_id: repoId, question }),
};
