import { Router, type IRouter, type Request, type Response } from "express";
import { store } from "../lib/store.js";
import { authenticate } from "../middlewares/authenticate.js";

const router: IRouter = Router();

router.use("/products", authenticate);

router.get("/products", (req: Request, res: Response) => {
  const page = Math.max(1, parseInt(String(req.query["page"] ?? "1"), 10) || 1);
  const perPage = Math.max(1, parseInt(String(req.query["per_page"] ?? "20"), 10) || 20);
  const { data, total } = store.listProducts(page, perPage);
  const totalPages = Math.ceil(total / perPage);
  res.status(200).json({
    data,
    total,
    page,
    per_page: perPage,
    total_pages: totalPages,
  });
});

router.get("/products/:id", (req: Request, res: Response) => {
  const id = parseInt(req.params["id"] ?? "", 10);
  if (isNaN(id)) {
    res.status(400).json({ error: "Bad Request", message: "Invalid product ID" });
    return;
  }
  const product = store.findProductById(id);
  if (!product) {
    res.status(404).json({ error: "Not Found", message: `Product ${id} not found` });
    return;
  }
  res.status(200).json(product);
});

router.post("/products", (req: Request, res: Response) => {
  const { name, description, price, stock } = req.body ?? {};

  if (!name || price === undefined || price === null) {
    res.status(422).json({
      error: "Unprocessable Entity",
      message: "name and price are required",
    });
    return;
  }

  const priceNum = Number(price);
  if (isNaN(priceNum) || priceNum < 0) {
    res.status(422).json({
      error: "Unprocessable Entity",
      message: "price must be a non-negative number",
    });
    return;
  }

  const stockNum = stock !== undefined && stock !== null ? Number(stock) : null;
  const product = store.createProduct(
    String(name),
    description !== undefined ? String(description) : null,
    priceNum,
    stockNum,
  );
  res.status(201).json(product);
});

router.put("/products/:id", (req: Request, res: Response) => {
  const id = parseInt(req.params["id"] ?? "", 10);
  if (isNaN(id)) {
    res.status(400).json({ error: "Bad Request", message: "Invalid product ID" });
    return;
  }
  if (!store.findProductById(id)) {
    res.status(404).json({ error: "Not Found", message: `Product ${id} not found` });
    return;
  }
  const { name, description, price, stock } = req.body ?? {};
  const fields: Parameters<typeof store.updateProduct>[1] = {};
  if (name !== undefined) fields.name = String(name);
  if (description !== undefined) fields.description = String(description);
  if (price !== undefined) {
    const priceNum = Number(price);
    if (isNaN(priceNum) || priceNum < 0) {
      res.status(422).json({ error: "Unprocessable Entity", message: "price must be a non-negative number" });
      return;
    }
    fields.price = priceNum;
  }
  if (stock !== undefined) fields.stock = stock !== null ? Number(stock) : null;
  const updated = store.updateProduct(id, fields);
  res.status(200).json(updated);
});

router.delete("/products/:id", (req: Request, res: Response) => {
  const id = parseInt(req.params["id"] ?? "", 10);
  if (isNaN(id)) {
    res.status(400).json({ error: "Bad Request", message: "Invalid product ID" });
    return;
  }
  if (!store.findProductById(id)) {
    res.status(404).json({ error: "Not Found", message: `Product ${id} not found` });
    return;
  }
  store.deleteProduct(id);
  res.status(204).send();
});

export default router;
