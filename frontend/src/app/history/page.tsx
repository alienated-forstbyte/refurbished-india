"use client";

import { useState } from "react";
import PriceChart from "@/components/PriceChart";
import type { ProductHistory } from "@/types";

export default function HistoryPage() {
  const [productId, setProductId] = useState("");
  const [history, setHistory] = useState<ProductHistory | null>(null);

  const loadHistory = async () => {
    const id = parseInt(productId, 10);
    if (isNaN(id)) return;
    try {
      const { getProductHistory } = await import("@/lib/api");
      const h = await getProductHistory(id);
      setHistory(h);
    } catch {
      setHistory(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Price History</h1>
      <div className="flex gap-2 mb-6">
        <input
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
          placeholder="Product ID"
          className="flex-1 px-4 py-2 border rounded text-sm"
        />
        <button onClick={loadHistory} className="bg-primary-600 text-white px-4 py-2 rounded text-sm">
          View History
        </button>
      </div>
      {history && (
        <div className="space-y-6">
          <PriceChart history={history.price_history} />
          {history.stock_history.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h2 className="font-semibold mb-3">Stock Changes</h2>
              <div className="space-y-1">
                {history.stock_history.map((sh, i) => (
                  <div key={i} className="flex justify-between text-sm">
                    <span className={sh.stock_status === "in_stock" ? "text-green-600" : "text-red-600"}>
                      {sh.stock_status}
                    </span>
                    <span className="text-gray-400">{new Date(sh.timestamp).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
