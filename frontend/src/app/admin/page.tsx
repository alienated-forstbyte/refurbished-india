"use client";

import { useEffect, useState } from "react";
import type { Store, Stats } from "@/types";

export default function AdminPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [{ getStores, getStats }] = await Promise.all([import("@/lib/api")]);
        const [s, st] = await Promise.all([getStores(), getStats()]);
        setStores(s);
        setStats(st);
      } catch {
        // API unavailable
      }
    })();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Products" value={stats.total_products} />
          <StatCard label="In Stock" value={stats.in_stock_count} />
          <StatCard label="Out of Stock" value={stats.out_of_stock_count} />
          <StatCard label="Stores" value={stats.store_count} />
        </div>
      )}

      <section>
        <h2 className="text-lg font-semibold mb-3">Stores</h2>
        <div className="bg-white rounded-lg border border-gray-200">
          {stores.length === 0 && <p className="p-4 text-gray-400 text-sm">No stores configured.</p>}
          {stores.map((store) => (
            <div key={store.id} className="flex items-center justify-between p-4 border-b last:border-b-0">
              <div>
                <div className="font-medium">{store.name}</div>
                <div className="text-sm text-gray-500">{store.website}</div>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <span className={store.enabled ? "text-green-600" : "text-red-600"}>
                  {store.enabled ? "Enabled" : "Disabled"}
                </span>
                {store.last_scrape && (
                  <span className="text-gray-400">Last: {new Date(store.last_scrape).toLocaleDateString()}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="text-2xl font-bold text-primary-600">{value.toLocaleString()}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
