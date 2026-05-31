import { clearToken, getToken } from "./auth-storage";
import type {
  PaginatedBars,
  PaginatedInstruments,
  PaginatedSignals,
  TokenResponse,
  User,
} from "./types";
import { ApiError } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function parseError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((d: { msg?: string }) => d.msg ?? "Error").join(", ");
    }
    return response.statusText || "Request failed";
  } catch {
    return response.statusText || "Request failed";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  authenticated = true,
): Promise<T> {
  const headers = new Headers(options.headers);

  if (authenticated) {
    const token = getToken();
    if (!token) {
      throw new ApiError("Not authenticated", 401);
    }
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !(options.body instanceof URLSearchParams) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401 && authenticated) {
      clearToken();
    }
    throw new ApiError(await parseError(response), response.status);
  }

  return response.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ username: email, password });
  return request<TokenResponse>("/auth/jwt/login", { method: "POST", body }, false);
}

export async function register(email: string, password: string): Promise<User> {
  return request<User>(
    "/auth/register",
    { method: "POST", body: JSON.stringify({ email, password }) },
    false,
  );
}

export async function getCurrentUser(): Promise<User> {
  return request<User>("/users/me");
}

export async function listInstruments(params: {
  q?: string;
  region?: string;
  limit?: number;
} = {}): Promise<PaginatedInstruments> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.region) search.set("region", params.region);
  if (params.limit) search.set("limit", String(params.limit));
  const query = search.toString();
  return request<PaginatedInstruments>(`/instruments${query ? `?${query}` : ""}`);
}

export async function getInstrumentBars(
  instrumentId: number,
  limit = 120,
): Promise<PaginatedBars> {
  return request<PaginatedBars>(`/instruments/${instrumentId}/bars?limit=${limit}`);
}

export async function listSignals(params: {
  watchlist?: string;
  strategy?: string;
  limit?: number;
} = {}): Promise<PaginatedSignals> {
  const search = new URLSearchParams();
  if (params.watchlist) search.set("watchlist", params.watchlist);
  if (params.strategy) search.set("strategy", params.strategy);
  if (params.limit) search.set("limit", String(params.limit));
  const query = search.toString();
  return request<PaginatedSignals>(`/signals${query ? `?${query}` : ""}`);
}
