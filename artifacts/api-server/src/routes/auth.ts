import { Router, type IRouter, type Request, type Response } from "express";
import { store } from "../lib/store.js";
import { signToken, TOKEN_EXPIRES_IN } from "../lib/jwt.js";

const router: IRouter = Router();

router.post("/auth/login", (req: Request, res: Response) => {
  const { username, password } = req.body ?? {};

  if (!username || !password) {
    res.status(422).json({
      error: "Unprocessable Entity",
      message: "username and password are required",
    });
    return;
  }

  const user = store.findUserByUsername(String(username));
  if (!user || !store.checkPassword(user, String(password))) {
    res.status(401).json({
      error: "Unauthorized",
      message: "Invalid username or password",
    });
    return;
  }

  const token = signToken({ sub: user.id, username: user.username });
  res.status(200).json({
    token,
    token_type: "Bearer",
    expires_in: TOKEN_EXPIRES_IN,
  });
});

export default router;
