import Link from "next/link";
import type { Product } from "@/types";
import StockBadge from "./StockBadge";
import DiscountBadge from "./DiscountBadge";

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  return (
    <Link
      href={`/product/${product.id}`}
      className="block bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
    >
      <div className="aspect-video bg-gray-100 rounded-t-lg flex items-center justify-center overflow-hidden">
        {product.image_url ? (
          <img src={product.image_url} alt={product.product_name || ""} className="object-cover w-full h-full" />
        ) : (
          <span className="text-gray-400 text-sm">No image</span>
        )}
      </div>
      <div className="p-4 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-gray-500 uppercase">{product.brand || "Unknown"}</span>
          <StockBadge status={product.stock_status} />
        </div>
        <h3 className="font-medium text-sm line-clamp-2">{product.product_name || "Unknown Product"}</h3>
        <div className="flex items-baseline gap-2">
          <span className="text-lg font-bold">₹{product.price?.toLocaleString("en-IN")}</span>
          {product.original_price && product.original_price > product.price! && (
            <span className="text-sm text-gray-400 line-through">₹{product.original_price.toLocaleString("en-IN")}</span>
          )}
          <DiscountBadge discount={product.discount} />
        </div>
        <div className="flex gap-2 text-xs text-gray-500">
          {product.cpu && <span>{product.cpu}</span>}
          {product.ram_gb && <span>{product.ram_gb}GB</span>}
          {product.storage_gb && <span>{product.storage_gb}GB</span>}
        </div>
      </div>
    </Link>
  );
}
