import { Router, type IRouter, type Request, type Response } from "express";
import { store } from "../lib/store.js";
import { authenticate } from "../middlewares/authenticate.js";

const router: IRouter = Router();

function serializeUser(user: ReturnType<typeof store.findUserById>) {
  if (!user) return null;
  const { passwordHash: _, ...rest } = user;
  return rest;
}

router.use("/users", authenticate);

router.get("/users", (req: Request, res: Response) => {
  const page = Math.max(1, parseInt(String(req.query["page"] ?? "1"), 10) || 1);
  const perPage = Math.max(1, parseInt(String(req.query["per_page"] ?? "20"), 10) || 20);
  const { data, total } = store.listUsers(page, perPage);
  const totalPages = Math.ceil(total / perPage);
  res.status(200).json({
    data: data.map(serializeUser),
    total,
    page,
    per_page: perPage,
    total_pages: totalPages,
  });
});

router.get("/users/:id", (req: Request, res: Response) => {
  const id = parseInt(req.params["id"] ?? "", 10);
  if (isNaN(id)) {
    res.status(400).json({ error: "Bad Request", message: "Invalid user ID" });
    return;
  }
  const user = store.findUserById(id);
  if (!user) {
    res.status(404).json({ error: "Not Found", message: `User ${id} not found` });
    return;
  }
  res.status(200).json(serializeUser(user));
});

router.post("/users", (req: Request, res: Response) => {
  const { username, email, password } = req.body ?? {};

  if (!username || !email || !password) {
    res.status(422).json({
      error: "Unprocessable Entity",
      message: "username, email, and password are required",
    });
    return;
  }

  if (store.findUserByEmail(String(email))) {
    res.status(409).json({ error: "Conflict", message: "Email already registered" });
    return;
  }

  if (store.findUserByUsername(String(username))) {
    res.status(409).json({ error: "Conflict", message: "Username already taken" });
    return;
  }

  const user = store.createUser(String(username), String(email), String(password));
  res.status(201).json(serializeUser(user));
});

router.put("/users/:id", (req: Request, res: Response) => {
  const id = parseInt(req.params["id"] ?? "", 10);
  if (isNaN(id)) {
    res.status(400).json({ error: "Bad Request", message: "Invalid user ID" });
    return;
  }
  if (!store.findUserById(id)) {
    res.status(404).json({ error: "Not Found", message: `User ${id} not found` });
    return;
  }
  const { username, email, password } = req.body ?? {};
  const updated = store.updateUser(id, {
    ...(username !== undefined ? { username: String(username) } : {}),
    ...(email !== undefined ? { email: String(email) } : {}),
    ...(password !== undefined ? { password: String(password) } : {}),
  });
  res.status(200).json(serializeUser(updated));
});

router.delete("/users/:id", (req: Request, res: Response) => {
  const id = parseInt(req.params["id"] ?? "", 10);
  if (isNaN(id)) {
    res.status(400).json({ error: "Bad Request", message: "Invalid user ID" });
    return;
  }
  if (!store.findUserById(id)) {
    res.status(404).json({ error: "Not Found", message: `User ${id} not found` });
    return;
  }
  store.deleteUser(id);
  res.status(204).send();
});

export default router;
