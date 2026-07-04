export interface Product {
  id: number;
  store_id: number;
  brand: string | null;
  model: string | null;
  product_name: string | null;
  cpu: string | null;
  cpu_generation: string | null;
  ram_gb: number | null;
  storage_gb: number | null;
  storage_type: string | null;
  gpu: string | null;
  display_size: number | null;
  display_resolution: string | null;
  condition: string | null;
  warranty_months: number | null;
  price: number | null;
  original_price: number | null;
  discount: number | null;
  currency: string;
  stock_status: string;
  product_url: string | null;
  image_url: string | null;
  first_seen: string;
  last_seen: string;
  last_updated: string;
}

export interface ProductList {
  total: number;
  page: number;
  limit: number;
  products: Product[];
}

export interface Store {
  id: number;
  name: string;
  website: string;
  country: string;
  enabled: boolean;
  last_scrape: string | null;
  scrape_interval: number;
}

export interface PriceHistoryEntry {
  price: number;
  timestamp: string;
}

export interface StockHistoryEntry {
  stock_status: string;
  timestamp: string;
}

export interface ProductHistory {
  price_history: PriceHistoryEntry[];
  stock_history: StockHistoryEntry[];
}

export interface Stats {
  total_products: number;
  in_stock_count: number;
  out_of_stock_count: number;
  store_count: number;
  average_price: number | null;
}

export interface Alert {
  id: number;
  user_id: number;
  brand: string | null;
  cpu: string | null;
  max_price: number | null;
  ram: number | null;
  storage: number | null;
  gpu: string | null;
  notify_stock: boolean;
  notify_price: boolean;
  enabled: boolean;
  created_at: string;
}

export interface AlertCreate {
  brand?: string | null;
  cpu?: string | null;
  max_price?: number | null;
  ram?: number | null;
  storage?: number | null;
  gpu?: string | null;
  notify_stock?: boolean;
  notify_price?: boolean;
}
