// src/auth/login.ts
import { hashPassword, comparePassword } from "../utils/crypto";
import { createSession } from "./session";
import { findUserByEmail } from "../api/users";
import type { LoginResult, Credentials } from "../api/types";

export async function login(credentials: Credentials): Promise<LoginResult> {
  const user = await findUserByEmail(credentials.email);

  if (!user) {
    return { success: false, error: "USER_NOT_FOUND" };
  }

  const valid = await comparePassword(credentials.password, user.passwordHash);
  if (!valid) {
    return { success: false, error: "INVALID_PASSWORD" };
  }

  const session = await createSession(user.id);
  return { success: true, token: session.token, userId: user.id };
}

export async function logout(token: string): Promise<void> {
  // TODO: invalidate session
}
