import clsx from "clsx";

interface StockBadgeProps {
  status: string;
  lastSeen?: string | null;
}

function hoursSince(dateStr: string | null | undefined): number | null {
  if (!dateStr) return null;
  const diff = Date.now() - new Date(dateStr).getTime();
  return Math.floor(diff / 3600000);
}

function formatAgo(hours: number): string {
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function StockBadge({ status, lastSeen }: StockBadgeProps) {
  const hours = hoursSince(lastSeen);
  const stale = hours !== null && hours >= 24;

  const colors: Record<string, string> = {
    in_stock: stale ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800",
    out_of_stock: "bg-red-100 text-red-800",
    unknown: "bg-gray-100 text-gray-600",
    removed: "bg-yellow-100 text-yellow-800",
  };

  const labels: Record<string, string> = {
    in_stock: stale ? "May be sold out" : "In Stock",
    out_of_stock: "Out of Stock",
    unknown: "Unknown",
    removed: "Removed",
  };

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium",
        colors[status] || colors.unknown
      )}
    >
      {labels[status] || status}
      {lastSeen && status === "in_stock" && (
        <span className="opacity-60">· {formatAgo(hours!)}</span>
      )}
    </span>
  );
}
