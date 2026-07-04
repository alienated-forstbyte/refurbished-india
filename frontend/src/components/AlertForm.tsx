"use client";

import { useState } from "react";

interface AlertFormProps {
  onCreated: () => void;
}

export default function AlertForm({ onCreated }: AlertFormProps) {
  const [brand, setBrand] = useState("");
  const [cpu, setCpu] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [ram, setRam] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const { createAlert } = await import("@/lib/api");
    await createAlert({
      brand: brand || undefined,
      cpu: cpu || undefined,
      max_price: maxPrice ? Number(maxPrice) : undefined,
      ram: ram ? Number(ram) : undefined,
    });
    onCreated();
    setBrand("");
    setCpu("");
    setMaxPrice("");
    setRam("");
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-4 space-y-3">
      <h3 className="font-medium text-sm">Create Alert</h3>
      <div className="grid grid-cols-2 gap-3">
        <input value={brand} onChange={(e) => setBrand(e.target.value)} placeholder="Brand" className="px-3 py-2 border rounded text-sm" />
        <input value={cpu} onChange={(e) => setCpu(e.target.value)} placeholder="CPU (e.g. i7)" className="px-3 py-2 border rounded text-sm" />
        <input value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} type="number" placeholder="Max Price (₹)" className="px-3 py-2 border rounded text-sm" />
        <input value={ram} onChange={(e) => setRam(e.target.value)} type="number" placeholder="RAM (GB)" className="px-3 py-2 border rounded text-sm" />
      </div>
      <button type="submit" className="w-full bg-primary-600 text-white py-2 rounded text-sm font-medium hover:bg-primary-700 transition">
        Create Alert
      </button>
    </form>
  );
}
