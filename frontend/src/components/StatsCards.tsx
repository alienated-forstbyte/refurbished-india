import type { Stats } from "@/types";

interface StatsCardsProps {
  stats: Stats | null;
}

export default function StatsCards({ stats }: StatsCardsProps) {
  if (!stats) return null;
  const cards = [
    { label: "Products Tracked", value: stats.total_products.toLocaleString() },
    { label: "In Stock", value: stats.in_stock_count.toLocaleString() },
    { label: "Out of Stock", value: stats.out_of_stock_count.toLocaleString() },
    { label: "Stores", value: stats.store_count },
    { label: "Avg Price", value: stats.average_price ? `₹${Math.round(stats.average_price).toLocaleString("en-IN")}` : "N/A" },
  ];
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      {cards.map((card) => (
        <div key={card.label} className="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div className="text-2xl font-bold text-primary-600">{card.value}</div>
          <div className="text-xs text-gray-500 mt-1">{card.label}</div>
        </div>
      ))}
    </div>
  );
}
