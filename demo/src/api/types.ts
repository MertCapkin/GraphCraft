// src/api/types.ts
export interface Credentials {
  email: string;
  password: string;
}

export interface LoginResult {
  success: boolean;
  token?: string;
  userId?: string;
  error?: "USER_NOT_FOUND" | "INVALID_PASSWORD" | "SESSION_ERROR";
}

export interface User {
  id: string;
  email: string;
  passwordHash: string;
  createdAt: Date;
}
