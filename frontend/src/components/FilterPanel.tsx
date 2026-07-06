"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Filter, X } from "lucide-react";
import type { Store } from "@/types";

export default function FilterPanel() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [stores, setStores] = useState<Store[]>([]);

  const [brand, setBrand] = useState(searchParams.get("brand") || "");
  const [stock, setStock] = useState(searchParams.get("stock") || "");
  const [priceMin, setPriceMin] = useState(searchParams.get("price_min") || "");
  const [priceMax, setPriceMax] = useState(searchParams.get("price_max") || "");
  const [ram, setRam] = useState(searchParams.get("ram") || "");
  const [storageMin, setStorageMin] = useState(searchParams.get("storage_min") || "");
  const [storageMax, setStorageMax] = useState(searchParams.get("storage_max") || "");
  const [storageType, setStorageType] = useState(searchParams.get("storage_type") || "");
  const [displaySizeMin, setDisplaySizeMin] = useState(searchParams.get("display_size_min") || "");
  const [displaySizeMax, setDisplaySizeMax] = useState(searchParams.get("display_size_max") || "");
  const [condition, setCondition] = useState(searchParams.get("condition") || "");
  const [cpuGeneration, setCpuGeneration] = useState(searchParams.get("cpu_generation") || "");
  const [storeId, setStoreId] = useState(searchParams.get("store_id") || "");
  const [warrantyMin, setWarrantyMin] = useState(searchParams.get("warranty_min") || "");
  const [sort, setSort] = useState(searchParams.get("sort") || "");

  useEffect(() => {
    import("@/lib/api").then(({ getStores }) => getStores().then(setStores).catch(() => {}));
  }, []);

  const applyFilters = () => {
    const params = new URLSearchParams();
    if (brand) params.set("brand", brand);
    if (stock) params.set("stock", stock);
    if (priceMin) params.set("price_min", priceMin);
    if (priceMax) params.set("price_max", priceMax);
    if (ram) params.set("ram", ram);
    if (storageMin) params.set("storage_min", storageMin);
    if (storageMax) params.set("storage_max", storageMax);
    if (storageType) params.set("storage_type", storageType);
    if (displaySizeMin) params.set("display_size_min", displaySizeMin);
    if (displaySizeMax) params.set("display_size_max", displaySizeMax);
    if (condition) params.set("condition", condition);
    if (cpuGeneration) params.set("cpu_generation", cpuGeneration);
    if (storeId) params.set("store_id", storeId);
    if (warrantyMin) params.set("warranty_min", warrantyMin);
    if (sort) params.set("sort", sort);
    router.push(`/products?${params}`);
  };

  const clearFilters = () => {
    router.push("/products");
  };

  const hasFilters = [...searchParams.keys()].length > 0;

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
            <label className="text-xs text-gray-500">Sort By</label>
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded text-sm"
            >
              <option value="">Default (Recently Updated)</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="discount_desc">Discount: High to Low</option>
              <option value="discount_asc">Discount: Low to High</option>
              <option value="newest">Newest First</option>
              <option value="updated">Recently Updated</option>
              <option value="name">Name A-Z</option>
              <option value="name_desc">Name Z-A</option>
              <option value="ram_desc">RAM: High to Low</option>
              <option value="ram_asc">RAM: Low to High</option>
              <option value="storage_desc">Storage: High to Low</option>
              <option value="storage_asc">Storage: Low to High</option>
              <option value="display_desc">Display: High to Low</option>
              <option value="display_asc">Display: Low to High</option>
            </select>
          </div>
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
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs text-gray-500">Min Storage (GB)</label>
              <input
                type="number"
                value={storageMin}
                onChange={(e) => setStorageMin(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded text-sm"
                placeholder="128"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500">Max Storage (GB)</label>
              <input
                type="number"
                value={storageMax}
                onChange={(e) => setStorageMax(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded text-sm"
                placeholder="2048"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-gray-500">Storage Type</label>
            <select
              value={storageType}
              onChange={(e) => setStorageType(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded text-sm"
            >
              <option value="">Any</option>
              <option value="SSD">SSD</option>
              <option value="HDD">HDD</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs text-gray-500">Min Display (inch)</label>
              <input
                type="number"
                step="0.1"
                value={displaySizeMin}
                onChange={(e) => setDisplaySizeMin(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded text-sm"
                placeholder="11.6"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500">Max Display (inch)</label>
              <input
                type="number"
                step="0.1"
                value={displaySizeMax}
                onChange={(e) => setDisplaySizeMax(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded text-sm"
                placeholder="17.3"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-gray-500">Condition</label>
            <input
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded text-sm"
              placeholder="Excellent, Good..."
            />
          </div>
          <div>
            <label className="text-xs text-gray-500">CPU Generation</label>
            <input
              value={cpuGeneration}
              onChange={(e) => setCpuGeneration(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded text-sm"
              placeholder="13th Gen, i7..."
            />
          </div>
          <div>
            <label className="text-xs text-gray-500">Store</label>
            <select
              value={storeId}
              onChange={(e) => setStoreId(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded text-sm"
            >
              <option value="">All Stores</option>
              {stores.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500">Min Warranty (months)</label>
            <input
              type="number"
              value={warrantyMin}
              onChange={(e) => setWarrantyMin(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded text-sm"
              placeholder="12"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={applyFilters}
              className="flex-1 bg-primary-600 text-white py-2 rounded text-sm font-medium hover:bg-primary-700 transition"
            >
              Apply Filters
            </button>
            {hasFilters && (
              <button
                onClick={clearFilters}
                className="px-3 py-2 border border-gray-300 rounded text-sm text-gray-600 hover:bg-gray-50 transition"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
