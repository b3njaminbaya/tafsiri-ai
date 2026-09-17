export const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export interface AuthUser {
  id: number;
  email: string;
  display_name?: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  role: { id: number; name: string } | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface SupportedLanguage {
  code: string;
  name: string;
  kenyan: boolean;
}

export interface RoadmapLanguage {
  code: string | null;
  name: string;
  family: string;
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

export const FORUM_CATEGORIES = [
  "general",
  "technical",
  "feature_requests",
  "model_training",
  "dataset_sharing",
] as const;

export type ForumCategory = (typeof FORUM_CATEGORIES)[number];

export interface ForumCategoryCount {
  category: ForumCategory;
  post_count: number;
}

export interface ForumPost {
  id: number;
  category: ForumCategory;
  title: string;
  author_handle: string;
  reply_count: number;
  created_at: string;
}

export interface ForumReply {
  id: number;
  post_id: number;
  author_handle: string;
  body: string;
  created_at: string;
}

export interface ForumPostDetail {
  id: number;
  category: ForumCategory;
  title: string;
  body: string;
  author_handle: string;
  created_at: string;
  replies: ForumReply[];
}

export type BlogPostStatus = "draft" | "published";

export interface BlogPost {
  id: number;
  slug: string;
  title: string;
  excerpt?: string | null;
  category?: string | null;
  status: BlogPostStatus;
  author_handle: string;
  published_at?: string | null;
  created_at: string;
}

export interface BlogPostDetail extends BlogPost {
  body: string;
}

export interface BlogPostInput {
  title: string;
  excerpt?: string | null;
  body: string;
  category?: string | null;
  status?: BlogPostStatus;
}

export interface AdminUser {
  id: number;
  email: string;
  display_name?: string | null;
  role: { id: number; name: string } | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface GlossaryTerm {
  id: number;
  domain: string;
  source_lang: string;
  target_lang: string;
  source_term: string;
  target_term: string;
  created_by_id?: number | null;
  created_at: string;
}

export interface GlossaryTermInput {
  domain: string;
  source_lang: string;
  target_lang: string;
  source_term: string;
  target_term: string;
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

export interface GlobalAnalyticsSummary extends AnalyticsSummary {
  total_users: number;
  total_datasets: number;
}

export interface PrivacySettings {
  analytics: boolean;
  marketing: boolean;
  functional: boolean;
  email_marketing: boolean;
  sms_marketing: boolean;
  push_notifications: boolean;
  data_collection: boolean;
  location_tracking: boolean;
  third_party_sharing: boolean;
}

export type GdprRequestType =
  | "access"
  | "rectification"
  | "erasure"
  | "restrict"
  | "portability"
  | "object";

export interface GdprRequestRecord {
  id: number;
  request_type: GdprRequestType;
  description?: string | null;
  status: "pending" | "completed";
  created_at: string;
  resolved_at?: string | null;
}

export interface Plan {
  price_id: string;
  quota_limit: number;
}

export interface ApiKey {
  id: number;
  key_prefix: string;
  is_active: boolean;
  quota_used: number;
  quota_limit?: number | null;
  created_at: string;
}

export interface ApiKeyCreateResponse {
  message: string;
  api_key: ApiKey;
  key: string;
}

export interface DataExport {
  user: AuthUser;
  translations: TranslationRecord[];
  feedback_given: FeedbackRecord[];
  corrections_given: CorrectionRecord[];
  datasets_uploaded: DatasetRecord[];
  api_keys: ApiKey[];
}

export interface ContactMessageInput {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export interface DependencyStatus {
  status: "operational" | "degraded" | "down";
  detail?: string | null;
}

export interface SystemStatus {
  status: "operational" | "degraded" | "down";
  checked_at: string;
  dependencies: Record<string, DependencyStatus>;
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
    // Sends/receives the httpOnly auth cookie on every request, including
    // cross-origin ones (frontend and backend run on different ports in
    // dev) — this is what lets the SPA authenticate without ever holding a
    // JS-readable token. An explicit `token` is still supported for API/CLI
    // parity and overrides the cookie when both are present (matches the
    // backend's precedence).
    credentials: "include",
    headers: {
      ...(skipJsonContentType ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    // FastAPI error bodies are `{"detail": "..."}` — surface that message
    // directly instead of the raw JSON blob, which every error toast in
    // this app would otherwise render verbatim (e.g. `{"detail":"Not
    // authenticated"}` shown as-is to the user).
    let message = text || `Request failed with status ${res.status}`;
    try {
      const parsed = JSON.parse(text);
      if (parsed && typeof parsed.detail === "string") {
        message = parsed.detail;
      }
    } catch {
      // Not JSON — keep the raw text as the message.
    }
    throw new ApiError(res.status, message);
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

  logout: () => request<{ message: string }>("/auth/logout", { method: "POST" }),

  me: (token?: string | null) => request<AuthUser>("/auth/me", {}, token),

  updateProfile: (payload: { display_name?: string | null }, token?: string | null) =>
    request<AuthUser>(
      "/auth/me",
      { method: "PATCH", body: JSON.stringify(payload) },
      token
    ),

  forgotPassword: (email: string) =>
    request<{ message: string }>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  resetPassword: (tokenValue: string, newPassword: string) =>
    request<{ message: string }>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ token: tokenValue, new_password: newPassword }),
    }),

  verifyEmail: (tokenValue: string) =>
    request<{ message: string }>("/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token: tokenValue }),
    }),

  resendVerification: (token?: string | null) =>
    request<{ message: string }>("/auth/resend-verification", { method: "POST" }, token),

  getOAuthProviders: () =>
    request<{ google: boolean; github: boolean }>("/auth/oauth/providers"),

  getPrivacySettings: (token?: string | null) =>
    request<PrivacySettings>("/privacy/settings", {}, token),

  updatePrivacySettings: (updates: Partial<PrivacySettings>, token?: string | null) =>
    request<PrivacySettings>(
      "/privacy/settings",
      { method: "PUT", body: JSON.stringify(updates) },
      token
    ),

  exportMyData: (token?: string | null) => request<DataExport>("/privacy/export", {}, token),

  deleteAccount: (token?: string | null) =>
    request<{ message: string }>("/privacy/delete-account", { method: "POST" }, token),

  submitGdprRequest: (
    payload: { request_type: GdprRequestType; description?: string },
    token?: string | null
  ) =>
    request<GdprRequestRecord>(
      "/privacy/gdpr-requests",
      { method: "POST", body: JSON.stringify(payload) },
      token
    ),

  listGdprRequests: (token?: string | null) =>
    request<GdprRequestRecord[]>("/privacy/gdpr-requests", {}, token),

  getLanguages: () => request<{ languages: SupportedLanguage[] }>("/languages"),

  getLanguagesRoadmap: () => request<{ languages: RoadmapLanguage[] }>("/languages/roadmap"),

  translate: (payload: TranslateRequest, token?: string | null) =>
    request<TranslateResponse>(
      "/translate/",
      { method: "POST", body: JSON.stringify(payload) },
      token
    ),

  translationHistory: (token?: string | null) =>
    request<TranslationRecord[]>("/translate/history", {}, token),

  submitFeedback: (
    translationId: number,
    payload: { rating: number; comment?: string },
    token?: string | null
  ) =>
    request<FeedbackRecord>(
      `/translate/${translationId}/feedback`,
      { method: "POST", body: JSON.stringify(payload) },
      token
    ),

  listDatasets: () => request<DatasetRecord[]>("/datasets/"),

  uploadDataset: (fields: DatasetUploadFields, token?: string | null) => {
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

  getReviewQueue: (token?: string | null, minConfidence = 0.6) =>
    request<TranslationRecord[]>(
      `/review/queue?min_confidence=${minConfidence}`,
      {},
      token
    ),

  submitCorrection: (
    translationId: number,
    payload: { corrected_text: string; note?: string },
    token?: string | null
  ) =>
    request<CorrectionRecord>(
      `/review/${translationId}/correct`,
      { method: "POST", body: JSON.stringify(payload) },
      token
    ),

  getCommunityStats: () => request<CommunityStats>("/community/stats"),

  getAnalyticsSummary: (token?: string | null) =>
    request<AnalyticsSummary>("/analytics/summary", {}, token),

  getGlobalAnalyticsSummary: (token?: string | null) =>
    request<GlobalAnalyticsSummary>("/analytics/global", {}, token),

  getPlans: () => request<Plan[]>("/billing/plans"),

  createCheckoutSession: (price_id: string) =>
    request<{ checkout_url: string }>("/billing/checkout-session", {
      method: "POST",
      body: JSON.stringify({ price_id }),
    }),

  getForumCategories: () => request<ForumCategoryCount[]>("/forum/categories"),

  listForumPosts: (category?: ForumCategory) =>
    request<ForumPost[]>(`/forum/posts${category ? `?category=${category}` : ""}`),

  getForumPost: (postId: number) => request<ForumPostDetail>(`/forum/posts/${postId}`),

  createForumPost: (payload: { category: ForumCategory; title: string; body: string }) =>
    request<ForumPost>("/forum/posts", { method: "POST", body: JSON.stringify(payload) }),

  createForumReply: (postId: number, payload: { body: string }) =>
    request<ForumReply>(`/forum/posts/${postId}/replies`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listBlogPosts: (category?: string) =>
    request<BlogPost[]>(`/blog/posts${category ? `?category=${encodeURIComponent(category)}` : ""}`),

  getBlogPost: (slug: string) => request<BlogPostDetail>(`/blog/posts/${slug}`),

  adminListBlogPosts: () => request<BlogPost[]>("/blog/admin/posts"),

  adminGetBlogPost: (postId: number) => request<BlogPostDetail>(`/blog/admin/posts/${postId}`),

  adminCreateBlogPost: (payload: BlogPostInput) =>
    request<BlogPostDetail>("/blog/admin/posts", { method: "POST", body: JSON.stringify(payload) }),

  adminUpdateBlogPost: (postId: number, payload: Partial<BlogPostInput>) =>
    request<BlogPostDetail>(`/blog/admin/posts/${postId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  adminDeleteBlogPost: (postId: number) =>
    request<{ message: string }>(`/blog/admin/posts/${postId}`, { method: "DELETE" }),

  adminListUsers: () => request<AdminUser[]>("/admin/users"),

  adminUpdateUser: (userId: number, payload: { role_name?: string; is_active?: boolean }) =>
    request<AdminUser>(`/admin/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  listGlossaryTerms: (params?: { domain?: string; source_lang?: string; target_lang?: string }) => {
    const qs = new URLSearchParams();
    if (params?.domain) qs.set("domain", params.domain);
    if (params?.source_lang) qs.set("source_lang", params.source_lang);
    if (params?.target_lang) qs.set("target_lang", params.target_lang);
    const query = qs.toString();
    return request<GlossaryTerm[]>(`/glossary/${query ? `?${query}` : ""}`);
  },

  createGlossaryTerm: (payload: GlossaryTermInput) =>
    request<GlossaryTerm>("/glossary/", { method: "POST", body: JSON.stringify(payload) }),

  deleteGlossaryTerm: (termId: number) =>
    request<{ message: string }>(`/glossary/${termId}`, { method: "DELETE" }),

  submitContactMessage: (payload: ContactMessageInput) =>
    request<{ id: number }>("/contact/", { method: "POST", body: JSON.stringify(payload) }),

  getSystemStatus: () => request<SystemStatus>("/status"),

  listApiKeys: (token?: string | null) => request<ApiKey[]>("/auth/api-keys", {}, token),

  createApiKey: (token?: string | null) =>
    request<ApiKeyCreateResponse>("/auth/api-keys", { method: "POST" }, token),

  revokeApiKey: (keyId: number, token?: string | null) =>
    request<{ message: string }>(`/auth/api-keys/${keyId}/revoke`, { method: "POST" }, token),
};

export { ApiError };
