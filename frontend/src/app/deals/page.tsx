"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { Product } from "@/types";

const DEAL_LABELS = [
  { min: 80, label: "🔥 Hot Deal", class: "bg-green-100 text-green-700" },
  { min: 60, label: "⭐ Good Deal", class: "bg-blue-100 text-blue-700" },
  { min: 40, label: "Fair Deal", class: "bg-yellow-100 text-yellow-700" },
  { min: 0, label: "Overpriced", class: "bg-gray-100 text-gray-500" },
];

function hoursSince(dateStr: string | null | undefined): number | null {
  if (!dateStr) return null;
  return Math.floor((Date.now() - new Date(dateStr).getTime()) / 3600000);
}

function dealBadge(score: number | null) {
  if (score == null) return null;
  const entry = DEAL_LABELS.find((e) => score >= e.min) || DEAL_LABELS[DEAL_LABELS.length - 1];
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${entry.class}`}>
      {entry.label} ({score})
    </span>
  );
}

export default function DealsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [compareMode, setCompareMode] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const { getProducts } = await import("@/lib/api");
        const result = await getProducts({ sort: "deal_score_desc", limit: 50 });
        setProducts(result.products);
      } catch {
        setError("Failed to load deals");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const toggleSelect = (id: number) => {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else if (next.size < 4) next.add(id);
    setSelected(next);
  };

  const compareProducts = products.filter((p) => selected.has(p.id));

  const specs: { label: string; render: (p: Product) => string | null }[] = [
    { label: "Brand", render: (p) => p.brand },
    { label: "Model", render: (p) => p.model },
    { label: "Deal Score", render: (p) => (p.deal_score != null ? `${p.deal_score}/100` : null) },
    { label: "Price", render: (p) => (p.price != null ? `₹${p.price.toLocaleString("en-IN")}` : null) },
    { label: "Original Price", render: (p) => (p.original_price != null ? `₹${p.original_price.toLocaleString("en-IN")}` : null) },
    { label: "Discount", render: (p) => (p.discount != null ? `${p.discount}%` : null) },
    { label: "CPU", render: (p) => p.cpu },
    { label: "CPU Gen", render: (p) => p.cpu_generation },
    { label: "RAM", render: (p) => (p.ram_gb != null ? `${p.ram_gb}GB` : null) },
    { label: "Storage", render: (p) => (p.storage_gb != null ? `${p.storage_gb}GB` : null) },
    { label: "Storage Type", render: (p) => p.storage_type },
    { label: "GPU", render: (p) => p.gpu },
    { label: "Display", render: (p) => (p.display_size != null ? `${p.display_size}"` : null) },
    { label: "Condition", render: (p) => p.condition },
    { label: "Warranty", render: (p) => (p.warranty_months != null ? `${p.warranty_months}m` : null) },
    { label: "Store", render: (p) => p.store_name },
  ];

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-gray-400">Loading deals...</div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-red-400">{error}</div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Best Deals</h1>
        <button
          onClick={() => { setCompareMode(!compareMode); setSelected(new Set()); }}
          className={`px-4 py-2 rounded text-sm font-medium transition ${
            compareMode
              ? "bg-primary-600 text-white"
              : "bg-white border border-gray-300 text-gray-700 hover:border-gray-400"
          }`}
        >
          {compareMode ? "Done Comparing" : "Compare Products"}
        </button>
      </div>

      {compareMode && compareProducts.length > 0 && (
        <div className="mb-8 overflow-x-auto bg-white rounded-lg border border-gray-200">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left py-3 pr-4 pl-4 font-medium text-gray-500">Spec</th>
                {compareProducts.map((p) => (
                  <th key={p.id} className="text-left py-3 px-4 font-medium min-w-[160px]">
                    <div className="text-xs text-gray-400">{p.store_name || ""}</div>
                    <div className="truncate max-w-[200px]">{p.product_name || `Product ${p.id}`}</div>
                    {dealBadge(p.deal_score)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {specs.map((spec) => (
                <tr key={spec.label} className="border-b">
                  <td className="py-3 pr-4 pl-4 text-gray-500 whitespace-nowrap">{spec.label}</td>
                  {compareProducts.map((p) => (
                    <td key={p.id} className="py-3 px-4">{spec.render(p) || "-"}</td>
                  ))}
                </tr>
              ))}
              <tr className="border-b">
                <td className="py-3 pr-4 pl-4 text-gray-500 whitespace-nowrap">Link</td>
                {compareProducts.map((p) => (
                  <td key={p.id} className="py-3 px-4">
                    {p.product_url ? (
                      <a href={p.product_url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline text-xs">
                        View on Store &rarr;
                      </a>
                    ) : "-"}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {compareMode && (
        <p className="text-xs text-gray-400 mb-4">
          Select up to 4 products to compare. Click a product card to select/deselect.
        </p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {products.map((p) => {
          const isSelected = selected.has(p.id);
          return (
            <div
              key={p.id}
              onClick={() => compareMode && toggleSelect(p.id)}
              className={`bg-white rounded-lg border transition-all ${
                compareMode
                  ? isSelected
                    ? "border-primary-500 ring-2 ring-primary-200 cursor-pointer"
                    : "border-gray-200 cursor-pointer hover:border-gray-300"
                  : "border-gray-200"
              }`}
            >
              <a
                href={p.product_url || "#"}
                target={p.product_url ? "_blank" : undefined}
                rel={p.product_url ? "noopener noreferrer" : undefined}
                className="block p-4 space-y-2"
                onClick={(e) => compareMode && e.preventDefault()}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-gray-500 uppercase">{p.brand || "Unknown"}</span>
                  {(() => {
                    const hours = hoursSince(p.last_seen);
                    const stale = hours !== null && hours > 48;
                    if (p.stock_status === "in_stock") {
                      return (
                        <span
                          title={hours != null ? `Verified ${hours}h ago` : undefined}
                          className={`text-xs font-medium ${stale ? "text-yellow-600" : "text-green-600"}`}
                        >
                          {stale ? "May be sold out" : "In Stock"}
                        </span>
                      );
                    }
                    return <span className="text-xs text-red-500">Out of Stock</span>;
                  })()}
                </div>
                <h3 className="font-medium text-sm line-clamp-2">{p.product_name || "Unknown Product"}</h3>
                {dealBadge(p.deal_score)}
                <div className="flex items-baseline gap-2">
                  <span className="text-lg font-bold">₹{p.price?.toLocaleString("en-IN")}</span>
                  {p.original_price && p.original_price > p.price! && (
                    <span className="text-sm text-gray-400 line-through">₹{p.original_price.toLocaleString("en-IN")}</span>
                  )}
                </div>
                <div className="flex gap-2 text-xs text-gray-500 flex-wrap">
                  {p.store_name && <span>{p.store_name}</span>}
                  {p.cpu && <span>{p.cpu}</span>}
                  {p.ram_gb && <span>{p.ram_gb}GB</span>}
                  {p.storage_gb && <span>{p.storage_gb}GB</span>}
                </div>
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
}
