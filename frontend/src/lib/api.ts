import type { ProductList, Product, Store, ProductHistory, Stats, Alert, AlertCreate } from "@/types";

const BASE = "/api/v1";

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function getProducts(params: Record<string, string | number | undefined> = {}): Promise<ProductList> {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null) qs.set(k, String(v));
  });
  return fetchJson<ProductList>(`${BASE}/products?${qs}`);
}

export async function searchProducts(query: string, page = 1, limit = 24): Promise<ProductList> {
  return fetchJson<ProductList>(`${BASE}/products/search?query=${encodeURIComponent(query)}&page=${page}&limit=${limit}`);
}

export async function getProduct(id: number): Promise<Product> {
  return fetchJson<Product>(`${BASE}/products/${id}`);
}

export async function getStores(): Promise<Store[]> {
  return fetchJson<Store[]>(`${BASE}/stores`);
}

export async function getStore(id: number): Promise<Store> {
  return fetchJson<Store>(`${BASE}/stores/${id}`);
}

export async function getProductHistory(productId: number): Promise<ProductHistory> {
  return fetchJson<ProductHistory>(`${BASE}/history/${productId}`);
}

export async function getStats(): Promise<Stats> {
  return fetchJson<Stats>(`${BASE}/stats`);
}

export async function getAlerts(): Promise<Alert[]> {
  return fetchJson<Alert[]>(`${BASE}/alerts`);
}

export async function createAlert(data: AlertCreate): Promise<Alert> {
  return fetchJson<Alert>(`${BASE}/alerts`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteAlert(id: number): Promise<void> {
  return fetchJson<void>(`${BASE}/alerts/${id}`, { method: "DELETE" });
}
