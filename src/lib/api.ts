export const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export interface AuthUser {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
  role: { id: number; name: string } | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface TranslateRequest {
  text: string;
  source_lang?: string;
  target_lang: string;
  domain?: string;
}

export interface TranslateResponse {
  translation: string;
  source_lang?: string | null;
  target_lang: string;
  domain?: string | null;
  confidence: number;
}

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const isForm = options.body instanceof URLSearchParams;
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(isForm ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(res.status, text || `Request failed with status ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  register: (email: string, password: string) =>
    request<AuthUser>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    return request<TokenResponse>("/auth/login", { method: "POST", body: form });
  },

  me: (token: string) => request<AuthUser>("/auth/me", {}, token),

  translate: (payload: TranslateRequest, token: string) =>
    request<TranslateResponse>(
      "/translate/",
      { method: "POST", body: JSON.stringify(payload) },
      token
    ),
};

export { ApiError };
