// src/auth/session.ts
import { generateToken } from "../utils/crypto";

interface Session {
  token: string;
  userId: string;
  createdAt: Date;
  expiresAt: Date;
}

const sessions = new Map<string, Session>();

export async function createSession(userId: string): Promise<Session> {
  const token = generateToken();
  const session: Session = {
    token,
    userId,
    createdAt: new Date(),
    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24h
  };
  sessions.set(token, session);
  return session;
}

export async function validateSession(token: string): Promise<Session | null> {
  const session = sessions.get(token);
  if (!session) return null;
  if (session.expiresAt < new Date()) {
    sessions.delete(token);
    return null;
  }
  return session;
}

export async function destroySession(token: string): Promise<void> {
  sessions.delete(token);
}
