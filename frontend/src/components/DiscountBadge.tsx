interface DiscountBadgeProps {
  discount: number | null;
}

export default function DiscountBadge({ discount }: DiscountBadgeProps) {
  if (discount === null || discount === undefined) return null;
  const formatted = Math.round(discount);
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-orange-100 text-orange-800">
      {formatted}% off
    </span>
  );
}
