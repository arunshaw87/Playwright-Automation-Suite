import { createHmac, randomBytes } from "node:crypto";

const SECRET = process.env["JWT_SECRET"] ?? "e2e-framework-secret-key-do-not-use-in-production";
const EXPIRES_IN = 3600;

function base64url(input: string | Buffer): string {
  const buf = typeof input === "string" ? Buffer.from(input, "utf8") : input;
  return buf.toString("base64").replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

function base64urlDecode(input: string): string {
  const padded = input + "=".repeat((4 - (input.length % 4)) % 4);
  return Buffer.from(padded.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8");
}

export interface JwtPayload {
  sub: number;
  username: string;
  iat: number;
  exp: number;
  jti: string;
}

export function signToken(payload: Omit<JwtPayload, "iat" | "exp" | "jti">): string {
  const header = base64url(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const now = Math.floor(Date.now() / 1000);
  const fullPayload: JwtPayload = {
    ...payload,
    iat: now,
    exp: now + EXPIRES_IN,
    jti: randomBytes(8).toString("hex"),
  };
  const body = base64url(JSON.stringify(fullPayload));
  const sig = createHmac("sha256", SECRET).update(`${header}.${body}`).digest("base64url");
  return `${header}.${body}.${sig}`;
}

export function verifyToken(token: string): JwtPayload | null {
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  const [header, body, sig] = parts;
  const expectedSig = createHmac("sha256", SECRET).update(`${header}.${body}`).digest("base64url");
  if (sig !== expectedSig) return null;
  try {
    const payload = JSON.parse(base64urlDecode(body)) as JwtPayload;
    const now = Math.floor(Date.now() / 1000);
    if (payload.exp < now) return null;
    return payload;
  } catch {
    return null;
  }
}

export const TOKEN_EXPIRES_IN = EXPIRES_IN;
