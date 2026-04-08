import jwt from "jsonwebtoken";

const SECRET = process.env["JWT_SECRET"] ?? "e2e-framework-secret-key-do-not-use-in-production";
const EXPIRES_IN = 3600;

export interface JwtPayload {
  sub: number;
  username: string;
  iat: number;
  exp: number;
  jti?: string;
}

export function signToken(payload: Omit<JwtPayload, "iat" | "exp" | "jti">): string {
  return jwt.sign(payload, SECRET, { algorithm: "HS256", expiresIn: EXPIRES_IN });
}

export function verifyToken(token: string): JwtPayload | null {
  try {
    return jwt.verify(token, SECRET, { algorithms: ["HS256"] }) as unknown as JwtPayload;
  } catch {
    return null;
  }
}

export const TOKEN_EXPIRES_IN = EXPIRES_IN;
