"use client";

import { useEffect, useState } from "react";
import type { Product, ProductHistory } from "@/types";
import StockBadge from "@/components/StockBadge";
import DiscountBadge from "@/components/DiscountBadge";
import PriceChart from "@/components/PriceChart";

interface Props {
  product: Product;
}

export default function ProductDetailClient({ product }: Props) {
  const [history, setHistory] = useState<ProductHistory | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const { getProductHistory } = await import("@/lib/api");
        const h = await getProductHistory(product.id);
        setHistory(h);
      } catch {
        // no history
      }
    })();
  }, [product.id]);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{product.product_name || "Unknown Product"}</h1>
          <p className="text-sm text-gray-500 mt-1">{product.brand} — {product.model}</p>
        </div>
        <StockBadge status={product.stock_status} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
          <div className="flex items-baseline gap-3">
            <span className="text-3xl font-bold">₹{product.price?.toLocaleString("en-IN")}</span>
            {product.original_price && (
              <span className="text-lg text-gray-400 line-through">₹{product.original_price.toLocaleString("en-IN")}</span>
            )}
            <DiscountBadge discount={product.discount} />
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {product.cpu && <Spec label="CPU" value={product.cpu} />}
            {product.cpu_generation && <Spec label="Generation" value={product.cpu_generation} />}
            {product.ram_gb && <Spec label="RAM" value={`${product.ram_gb} GB`} />}
            {product.storage_gb && <Spec label="Storage" value={`${product.storage_gb} GB ${product.storage_type || ""}`} />}
            {product.gpu && <Spec label="GPU" value={product.gpu} />}
            {product.display_size && <Spec label="Display" value={`${product.display_size}" ${product.display_resolution || ""}`} />}
            {product.condition && <Spec label="Condition" value={product.condition} />}
            {product.warranty_months && <Spec label="Warranty" value={`${product.warranty_months} months`} />}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="font-semibold mb-4">Price History</h2>
          <PriceChart history={history?.price_history || []} />
        </div>
      </div>

      {product.product_url && (
        <a
          href={product.product_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block bg-primary-600 text-white px-6 py-2 rounded text-sm font-medium hover:bg-primary-700 transition"
        >
          View on Store
        </a>
      )}
    </div>
  );
}

function Spec({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-gray-500">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}
