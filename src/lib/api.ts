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
  id: number;
  translation: string;
  source_lang?: string | null;
  target_lang: string;
  domain?: string | null;
  confidence: number;
  applied_glossary_terms: string[];
}

export interface TranslationRecord {
  id: number;
  source_lang?: string | null;
  target_lang: string;
  domain?: string | null;
  input_text: string;
  output_text: string;
  confidence: number;
  created_at: string;
}

export interface FeedbackRecord {
  id: number;
  translation_id: number;
  rating: number;
  comment?: string | null;
  created_at: string;
}

export interface DatasetRecord {
  id: number;
  name: string;
  description?: string | null;
  source_lang?: string | null;
  target_lang?: string | null;
  domain?: string | null;
  size_bytes: number;
  uploaded_by_id: number;
  created_at: string;
}

export interface DatasetUploadFields {
  name: string;
  description?: string;
  source_lang?: string;
  target_lang?: string;
  domain?: string;
  file: File;
}

export interface CorrectionRecord {
  id: number;
  translation_id: number;
  reviewer_id: number;
  corrected_text: string;
  note?: string | null;
  created_at: string;
}

export interface ContributorCount {
  handle: string;
  count: number;
}

export interface CommunityStats {
  total_datasets: number;
  total_translations: number;
  total_corrections: number;
  total_contributors: number;
  top_dataset_contributors: ContributorCount[];
  top_reviewers: ContributorCount[];
}

export interface DailyCount {
  date: string;
  count: number;
}

export interface LanguagePairCount {
  source_lang?: string | null;
  target_lang: string;
  count: number;
}

export interface RatingBreakdown {
  rating: number;
  count: number;
}

export interface AnalyticsSummary {
  total_translations: number;
  average_confidence: number;
  translations_by_day: DailyCount[];
  top_language_pairs: LanguagePairCount[];
  feedback_breakdown: RatingBreakdown[];
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
  const skipJsonContentType =
    options.body instanceof URLSearchParams || options.body instanceof FormData;
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(skipJsonContentType ? {} : { "Content-Type": "application/json" }),
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

  translationHistory: (token: string) =>
    request<TranslationRecord[]>("/translate/history", {}, token),

  submitFeedback: (
    translationId: number,
    payload: { rating: number; comment?: string },
    token: string
  ) =>
    request<FeedbackRecord>(
      `/translate/${translationId}/feedback`,
      { method: "POST", body: JSON.stringify(payload) },
      token
    ),

  listDatasets: () => request<DatasetRecord[]>("/datasets/"),

  uploadDataset: (fields: DatasetUploadFields, token: string) => {
    const form = new FormData();
    form.set("name", fields.name);
    if (fields.description) form.set("description", fields.description);
    if (fields.source_lang) form.set("source_lang", fields.source_lang);
    if (fields.target_lang) form.set("target_lang", fields.target_lang);
    if (fields.domain) form.set("domain", fields.domain);
    form.set("file", fields.file);
    return request<DatasetRecord>(
      "/datasets/",
      { method: "POST", body: form },
      token
    );
  },

  getDatasetDownloadUrl: (datasetId: number) =>
    request<{ url: string; expires_in_seconds: number }>(
      `/datasets/${datasetId}/download`
    ),

  getReviewQueue: (token: string, minConfidence = 0.6) =>
    request<TranslationRecord[]>(
      `/review/queue?min_confidence=${minConfidence}`,
      {},
      token
    ),

  submitCorrection: (
    translationId: number,
    payload: { corrected_text: string; note?: string },
    token: string
  ) =>
    request<CorrectionRecord>(
      `/review/${translationId}/correct`,
      { method: "POST", body: JSON.stringify(payload) },
      token
    ),

  getCommunityStats: () => request<CommunityStats>("/community/stats"),

  getAnalyticsSummary: (token: string) =>
    request<AnalyticsSummary>("/analytics/summary", {}, token),
};

export { ApiError };
