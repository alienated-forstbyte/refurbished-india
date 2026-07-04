"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Filter, X } from "lucide-react";

export default function FilterPanel() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [open, setOpen] = useState(false);

  const [brand, setBrand] = useState(searchParams.get("brand") || "");
  const [stock, setStock] = useState(searchParams.get("stock") || "");
  const [priceMin, setPriceMin] = useState(searchParams.get("price_min") || "");
  const [priceMax, setPriceMax] = useState(searchParams.get("price_max") || "");
  const [ram, setRam] = useState(searchParams.get("ram") || "");

  const applyFilters = () => {
    const params = new URLSearchParams();
    if (brand) params.set("brand", brand);
    if (stock) params.set("stock", stock);
    if (priceMin) params.set("price_min", priceMin);
    if (priceMax) params.set("price_max", priceMax);
    if (ram) params.set("ram", ram);
    router.push(`/products?${params}`);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <button onClick={() => setOpen(!open)} className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
        <Filter className="w-4 h-4" />
        Filters
        {open && <X className="w-4 h-4 ml-auto" onClick={() => setOpen(false)} />}
      </button>
      {open && (
        <div className="space-y-3 mt-3">
          <div>
            <label className="text-xs text-gray-500">Brand</label>
            <input
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded text-sm"
              placeholder="Lenovo, Dell..."
            />
          </div>
          <div>
            <label className="text-xs text-gray-500">Stock</label>
            <select
              value={stock}
              onChange={(e) => setStock(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded text-sm"
            >
              <option value="">All</option>
              <option value="in_stock">In Stock</option>
              <option value="out_of_stock">Out of Stock</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs text-gray-500">Min Price</label>
              <input
                type="number"
                value={priceMin}
                onChange={(e) => setPriceMin(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded text-sm"
                placeholder="₹0"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500">Max Price</label>
              <input
                type="number"
                value={priceMax}
                onChange={(e) => setPriceMax(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded text-sm"
                placeholder="₹200000"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-gray-500">RAM (GB)</label>
            <select
              value={ram}
              onChange={(e) => setRam(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded text-sm"
            >
              <option value="">Any</option>
              <option value="4">4 GB</option>
              <option value="8">8 GB</option>
              <option value="16">16 GB</option>
              <option value="32">32 GB</option>
              <option value="64">64 GB</option>
            </select>
          </div>
          <button
            onClick={applyFilters}
            className="w-full bg-primary-600 text-white py-2 rounded text-sm font-medium hover:bg-primary-700 transition"
          >
            Apply Filters
          </button>
        </div>
      )}
    </div>
  );
}
