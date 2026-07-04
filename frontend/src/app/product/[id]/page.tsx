import { notFound } from "next/navigation";
import ProductDetailClient from "./ProductDetailClient";

interface Props {
  params: { id: string };
}

export default async function ProductDetailPage({ params }: Props) {
  const id = parseInt(params.id, 10);
  if (isNaN(id)) notFound();

  let product;
  try {
    const { getProduct } = await import("@/lib/api");
    product = await getProduct(id);
  } catch {
    notFound();
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <ProductDetailClient product={product} />
    </div>
  );
}
