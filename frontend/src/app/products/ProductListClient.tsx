"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import ProductCard from "@/components/ProductCard";
import FilterPanel from "@/components/FilterPanel";
import SearchBar from "@/components/SearchBar";
import type { ProductList } from "@/types";

export default function ProductListClient() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [data, setData] = useState<ProductList | null>(null);
  const page = Number(searchParams.get("page")) || 1;

  const fetchProducts = async () => {
    const { getProducts, searchProducts } = await import("@/lib/api");
    const search = searchParams.get("search");
    try {
      if (search) {
        const result = await searchProducts(search, page);
        setData(result);
      } else {
        const params: Record<string, string | number> = { page, limit: 24 };
        for (const key of ["brand", "stock", "price_min", "price_max", "ram", "cpu", "gpu", "sort", "storage_min", "storage_max", "storage_type", "display_size_min", "display_size_max", "condition", "cpu_generation", "store_id", "warranty_min"]) {
          const val = searchParams.get(key);
          if (val) params[key] = key === "sort" || key === "storage_type" || key === "condition" || key === "cpu_generation" || key === "brand" || key === "stock" || key === "cpu" || key === "gpu" ? val : Number(val);
        }
        const result = await getProducts(params);
        setData(result);
      }
    } catch {
      setData({ total: 0, page: 1, limit: 24, products: [] });
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [searchParams]);

  const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

  const currentSort = searchParams.get("sort") || "";

  const setSort = (sort: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.delete("page");
    if (sort) params.set("sort", sort);
    else params.delete("sort");
    router.push(`/products?${params}`);
  };

  const sortOptions = [
    { value: "deal_score_desc", label: "Best Deals" },
    { value: "price_asc", label: "Price: Low to High" },
    { value: "price_desc", label: "Price: High to Low" },
    { value: "discount_desc", label: "Discount: High to Low" },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <aside className="lg:col-span-1">
        <div className="mb-4">
          <SearchBar />
        </div>
        <FilterPanel />
      </aside>
      <main className="lg:col-span-3">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
          <span className="text-sm text-gray-500">
            {data ? `${data.total} products found` : "Loading..."}
          </span>
          <div className="flex gap-1">
            {sortOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setSort(opt.value)}
                className={`px-3 py-1.5 text-xs rounded border transition ${
                  currentSort === opt.value
                    ? "bg-primary-600 text-white border-primary-600"
                    : "bg-white text-gray-600 border-gray-300 hover:border-gray-400"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
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
              onClick={() => {
                const p = new URLSearchParams(searchParams.toString());
                p.set("page", String(page - 1));
                router.push(`/products?${p}`);
              }}
              className="px-4 py-2 border rounded text-sm disabled:opacity-40"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-sm text-gray-500">
              Page {page} of {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => {
                const p = new URLSearchParams(searchParams.toString());
                p.set("page", String(page + 1));
                router.push(`/products?${p}`);
              }}
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
