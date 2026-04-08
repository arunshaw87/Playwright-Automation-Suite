import { createHash } from "node:crypto";

export interface User {
  id: number;
  username: string;
  email: string;
  passwordHash: string;
  createdAt: string;
  updatedAt: string;
}

export interface Product {
  id: number;
  name: string;
  description: string | null;
  price: number;
  stock: number | null;
  createdAt: string;
  updatedAt: string;
}

function hashPassword(password: string): string {
  return createHash("sha256").update(password).digest("hex");
}

function now(): string {
  return new Date().toISOString();
}

class Store {
  private users: Map<number, User> = new Map();
  private products: Map<number, Product> = new Map();
  private userIdSeq = 1;
  private productIdSeq = 1;

  constructor() {
    this.seed();
  }

  private seed(): void {
    const ts = now();

    this.users.set(1, {
      id: 1,
      username: "admin",
      email: "admin@example.com",
      passwordHash: hashPassword("password"),
      createdAt: ts,
      updatedAt: ts,
    });
    this.userIdSeq = 2;

    const sampleProducts: Omit<Product, "id" | "createdAt" | "updatedAt">[] = [
      { name: "Widget Alpha", description: "A sturdy widget", price: 9.99, stock: 100 },
      { name: "Gadget Beta", description: "A compact gadget", price: 24.99, stock: 50 },
      { name: "Doohickey Gamma", description: "A versatile doohickey", price: 4.49, stock: 200 },
      { name: "Thingamajig Delta", description: "A reliable thingamajig", price: 14.99, stock: 75 },
      { name: "Whatchamacallit Epsilon", description: "An innovative whatchamacallit", price: 39.99, stock: 30 },
      { name: "Gizmo Zeta", description: null, price: 7.50, stock: 120 },
      { name: "Contraption Eta", description: "A complex contraption", price: 99.99, stock: 10 },
    ];

    for (const p of sampleProducts) {
      const id = this.productIdSeq++;
      this.products.set(id, { id, ...p, createdAt: ts, updatedAt: ts });
    }
  }

  findUserByUsername(username: string): User | undefined {
    for (const user of this.users.values()) {
      if (user.username === username) return user;
    }
  }

  findUserByEmail(email: string): User | undefined {
    for (const user of this.users.values()) {
      if (user.email === email) return user;
    }
  }

  findUserById(id: number): User | undefined {
    return this.users.get(id);
  }

  listUsers(page: number, perPage: number): { data: User[]; total: number } {
    const all = [...this.users.values()];
    const total = all.length;
    const data = all.slice((page - 1) * perPage, page * perPage);
    return { data, total };
  }

  createUser(username: string, email: string, password: string): User {
    const id = this.userIdSeq++;
    const ts = now();
    const user: User = {
      id,
      username,
      email,
      passwordHash: hashPassword(password),
      createdAt: ts,
      updatedAt: ts,
    };
    this.users.set(id, user);
    return user;
  }

  updateUser(id: number, fields: Partial<{ username: string; email: string; password: string }>): User | undefined {
    const user = this.users.get(id);
    if (!user) return undefined;
    if (fields.username !== undefined) user.username = fields.username;
    if (fields.email !== undefined) user.email = fields.email;
    if (fields.password !== undefined) user.passwordHash = hashPassword(fields.password);
    user.updatedAt = now();
    this.users.set(id, user);
    return user;
  }

  deleteUser(id: number): boolean {
    return this.users.delete(id);
  }

  checkPassword(user: User, password: string): boolean {
    return user.passwordHash === hashPassword(password);
  }

  findProductById(id: number): Product | undefined {
    return this.products.get(id);
  }

  listProducts(page: number, perPage: number): { data: Product[]; total: number } {
    const all = [...this.products.values()];
    const total = all.length;
    const data = all.slice((page - 1) * perPage, page * perPage);
    return { data, total };
  }

  createProduct(name: string, description: string | null, price: number, stock: number | null): Product {
    const id = this.productIdSeq++;
    const ts = now();
    const product: Product = { id, name, description, price, stock, createdAt: ts, updatedAt: ts };
    this.products.set(id, product);
    return product;
  }

  updateProduct(id: number, fields: Partial<{ name: string; description: string | null; price: number; stock: number | null }>): Product | undefined {
    const product = this.products.get(id);
    if (!product) return undefined;
    if (fields.name !== undefined) product.name = fields.name;
    if (fields.description !== undefined) product.description = fields.description;
    if (fields.price !== undefined) product.price = fields.price;
    if (fields.stock !== undefined) product.stock = fields.stock;
    product.updatedAt = now();
    this.products.set(id, product);
    return product;
  }

  deleteProduct(id: number): boolean {
    return this.products.delete(id);
  }
}

export const store = new Store();
