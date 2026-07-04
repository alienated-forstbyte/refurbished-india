import clsx from "clsx";

interface StockBadgeProps {
  status: string;
}

export default function StockBadge({ status }: StockBadgeProps) {
  const colors: Record<string, string> = {
    in_stock: "bg-green-100 text-green-800",
    out_of_stock: "bg-red-100 text-red-800",
    unknown: "bg-gray-100 text-gray-600",
    removed: "bg-yellow-100 text-yellow-800",
  };

  const labels: Record<string, string> = {
    in_stock: "In Stock",
    out_of_stock: "Out of Stock",
    unknown: "Unknown",
    removed: "Removed",
  };

  return (
    <span
      className={clsx(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        colors[status] || colors.unknown
      )}
    >
      {labels[status] || status}
    </span>
  );
}
