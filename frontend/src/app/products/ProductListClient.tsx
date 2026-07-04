"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import ProductCard from "@/components/ProductCard";
import FilterPanel from "@/components/FilterPanel";
import SearchBar from "@/components/SearchBar";
import type { ProductList } from "@/types";

export default function ProductListClient() {
  const searchParams = useSearchParams();
  const [data, setData] = useState<ProductList | null>(null);
  const [page, setPage] = useState(1);

  const fetchProducts = async () => {
    const { getProducts, searchProducts } = await import("@/lib/api");
    const search = searchParams.get("search");
    try {
      if (search) {
        const result = await searchProducts(search, page);
        setData(result);
      } else {
        const params: Record<string, string | number> = { page, limit: 24 };
        const brand = searchParams.get("brand");
        const stock = searchParams.get("stock");
        const priceMin = searchParams.get("price_min");
        const priceMax = searchParams.get("price_max");
        const ram = searchParams.get("ram");
        if (brand) params.brand = brand;
        if (stock) params.stock = stock;
        if (priceMin) params.price_min = priceMin;
        if (priceMax) params.price_max = priceMax;
        if (ram) params.ram = Number(ram);
        const result = await getProducts(params);
        setData(result);
      }
    } catch {
      setData({ total: 0, page: 1, limit: 24, products: [] });
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [searchParams, page]);

  const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <aside className="lg:col-span-1">
        <div className="mb-4">
          <SearchBar />
        </div>
        <FilterPanel />
      </aside>
      <main className="lg:col-span-3">
        <div className="flex justify-between items-center mb-4">
          <span className="text-sm text-gray-500">
            {data ? `${data.total} products found` : "Loading..."}
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {data?.products.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
        {totalPages > 1 && (
          <div className="flex justify-center gap-2 mt-8">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="px-4 py-2 border rounded text-sm disabled:opacity-40"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-sm text-gray-500">
              Page {page} of {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="px-4 py-2 border rounded text-sm disabled:opacity-40"
            >
              Next
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
