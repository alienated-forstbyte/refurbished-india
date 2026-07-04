"use client";

import { useState, useEffect } from "react";
import type { Product } from "@/types";

export default function ComparePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [ids, setIds] = useState("");

  const loadProducts = async () => {
    const nums = ids.split(",").map((s) => parseInt(s.trim(), 10)).filter((n) => !isNaN(n));
    if (nums.length === 0) return;
    const { getProduct } = await import("@/lib/api");
    const results = await Promise.allSettled(nums.map((id) => getProduct(id)));
    setProducts(results.filter((r) => r.status === "fulfilled").map((r) => (r as PromiseFulfilledResult<Product>).value));
  };

  const specs: { label: string; key: keyof Product }[] = [
    { label: "Brand", key: "brand" },
    { label: "Model", key: "model" },
    { label: "CPU", key: "cpu" },
    { label: "RAM", key: "ram_gb" },
    { label: "Storage", key: "storage_gb" },
    { label: "GPU", key: "gpu" },
    { label: "Display", key: "display_size" },
    { label: "Price", key: "price" },
    { label: "Discount", key: "discount" },
    { label: "Stock", key: "stock_status" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Compare Products</h1>
      <div className="flex gap-2 mb-6">
        <input
          value={ids}
          onChange={(e) => setIds(e.target.value)}
          placeholder="Product IDs: 1, 2, 3"
          className="flex-1 px-4 py-2 border rounded text-sm"
        />
        <button onClick={loadProducts} className="bg-primary-600 text-white px-4 py-2 rounded text-sm">
          Compare
        </button>
      </div>
      {products.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 pr-4 font-medium text-gray-500">Specification</th>
                {products.map((p) => (
                  <th key={p.id} className="text-left py-3 px-4 font-medium">{p.product_name || `Product ${p.id}`}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {specs.map((spec) => (
                <tr key={spec.key} className="border-b">
                  <td className="py-3 pr-4 text-gray-500">{spec.label}</td>
                  {products.map((p) => (
                    <td key={p.id} className="py-3 px-4">
                      {formatSpecValue(p[spec.key])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function formatSpecValue(value: unknown): string {
  if (value === null || value === undefined) return "-";
  if (typeof value === "number") {
    if (Number.isInteger(value)) return value.toLocaleString();
    return value.toFixed(1);
  }
  return String(value);
}
