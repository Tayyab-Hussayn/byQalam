export type UserRole = "owner" | "admin" | "editor" | "viewer";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  tenantId: string;
}

export interface SessionSummary {
  user: AuthUser;
  expiresAt: string;
}
