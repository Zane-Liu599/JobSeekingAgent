export type AuthUser = {
  id: number;
  name: string;
  email: string;
  phone: string;
  email_verified: boolean;
  created_at: string | null;
};

export type RegisterPayload = {
  name: string;
  email: string;
  phone: string;
  password: string;
};

export type RegisterResponse = {
  message: string;
  email: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

const apiBase = "/api/identity";
const tokenKey = "jobseekingAuthToken";
const userKey = "jobseekingAuthUser";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {})
    },
    ...options
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(errorMessage(body, response.statusText));
  }

  return response.json() as Promise<T>;
}

function errorMessage(body: string, fallback: string): string {
  if (!body) return fallback;
  try {
    const parsed = JSON.parse(body) as { detail?: unknown };
    if (typeof parsed.detail === "string") return parsed.detail;
    if (parsed.detail && typeof parsed.detail === "object" && "password" in parsed.detail) {
      const password = (parsed.detail as { password?: string[] }).password;
      if (Array.isArray(password)) return password.join(" ");
    }
    if (Array.isArray(parsed.detail)) {
      return parsed.detail.map((item) => item.msg ?? "Invalid input").join(" ");
    }
  } catch {
    return body;
  }
  return fallback;
}

export async function registerAccount(payload: RegisterPayload): Promise<RegisterResponse> {
  return request<RegisterResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function loginAccount(email: string, password: string): Promise<LoginResponse> {
  const response = await request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
  saveAuth(response.access_token, response.user);
  return response;
}

export async function verifyEmail(token: string) {
  return request<{ verified: boolean; message: string }>(
    `/auth/verify-email?token=${encodeURIComponent(token)}`
  );
}

export async function resendVerificationEmail(email: string) {
  return request<{ message: string; email: string; retry_after_seconds: number }>(
    "/auth/resend-verification",
    {
      method: "POST",
      body: JSON.stringify({ email })
    }
  );
}

export function saveAuth(token: string, user: AuthUser) {
  localStorage.setItem(tokenKey, token);
  localStorage.setItem(userKey, JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem(tokenKey);
  localStorage.removeItem(userKey);
}

export function getAuthToken(): string {
  return localStorage.getItem(tokenKey) || "";
}

export function getStoredUser(): AuthUser | null {
  const value = localStorage.getItem(userKey);
  if (!value) return null;
  try {
    return JSON.parse(value) as AuthUser;
  } catch {
    clearAuth();
    return null;
  }
}

export function passwordChecks(password: string) {
  return [
    { label: "At least 10 characters", passed: password.length >= 10 },
    { label: "Uppercase and lowercase letters", passed: /[A-Z]/.test(password) && /[a-z]/.test(password) },
    { label: "At least one number", passed: /\d/.test(password) },
    { label: "At least one symbol", passed: /[^A-Za-z0-9]/.test(password) }
  ];
}

export function passwordStrength(password: string): { label: string; score: number } {
  const score = passwordChecks(password).filter((item) => item.passed).length;
  if (!password) return { label: "Required", score: 0 };
  if (score <= 1) return { label: "Weak", score };
  if (score <= 3) return { label: "Medium", score };
  return { label: "Strong", score };
}

export function phoneValidationMessage(phone: string): string {
  const value = phone.trim();
  if (!value) return "Phone number is required.";
  if (!/^\+?[0-9][0-9 ()-]*$/.test(value)) {
    return "Use digits, spaces, brackets, dashes, and an optional leading + only.";
  }
  const digits = value.replace(/\D/g, "");
  if (digits.length < 8 || digits.length > 15) {
    return "Phone number must contain 8 to 15 digits.";
  }
  return "";
}
