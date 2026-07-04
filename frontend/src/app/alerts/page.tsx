"use client";

import { useEffect, useState } from "react";
import type { Alert } from "@/types";
import AlertForm from "@/components/AlertForm";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  const loadAlerts = async () => {
    try {
      const { getAlerts } = await import("@/lib/api");
      const result = await getAlerts();
      setAlerts(result);
    } catch {
      setAlerts([]);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleDelete = async (id: number) => {
    try {
      const { deleteAlert } = await import("@/lib/api");
      await deleteAlert(id);
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    } catch {
      // ignore
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Alerts</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <AlertForm onCreated={loadAlerts} />
        </div>
        <div className="md:col-span-2 space-y-3">
          {alerts.length === 0 && <p className="text-gray-400 text-sm">No alerts yet. Create one to get notified.</p>}
          {alerts.map((alert) => (
            <div key={alert.id} className="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between">
              <div className="text-sm">
                <div className="font-medium">
                  {[alert.brand, alert.cpu, alert.gpu].filter(Boolean).join(" · ") || "Any product"}
                </div>
                <div className="text-gray-500 mt-1">
                  {alert.max_price && `Max ₹${alert.max_price.toLocaleString("en-IN")}`}
                  {alert.ram && ` · ${alert.ram}GB RAM`}
                  {alert.storage && ` · ${alert.storage}GB Storage`}
                </div>
              </div>
              <button
                onClick={() => handleDelete(alert.id)}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
