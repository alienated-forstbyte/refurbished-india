import { Suspense } from "react";
import ProductListClient from "./ProductListClient";

export default function ProductsPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Products</h1>
      <Suspense fallback={<div className="text-gray-400">Loading...</div>}>
        <ProductListClient />
      </Suspense>
    </div>
  );
}
