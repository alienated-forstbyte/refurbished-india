"use client";

import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import type { PriceHistoryEntry } from "@/types";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface PriceChartProps {
  history: PriceHistoryEntry[];
}

export default function PriceChart({ history }: PriceChartProps) {
  if (!history || history.length === 0) {
    return <div className="text-gray-400 text-sm p-4 text-center">No price history available</div>;
  }

  const data = {
    labels: history.map((h) => new Date(h.timestamp).toLocaleDateString()),
    datasets: [
      {
        label: "Price (₹)",
        data: history.map((h) => h.price),
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        fill: true,
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <Line
        data={data}
        options={{
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { maxTicksLimit: 10 } },
            y: {
              ticks: { callback: (v) => `₹${v}` },
            },
          },
        }}
      />
    </div>
  );
}
