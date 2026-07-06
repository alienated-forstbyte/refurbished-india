# REST API

Base URL: `/api/v1`

---

## GET /products

Paginated product list with filtering and sorting.

### Parameters

| Param | Type | Description |
|---|---|---|
| `page` | int | Page number (default: 1) |
| `limit` | int | Results per page (default: 20) |
| `brand` | str | Filter by brand |
| `model` | str | Filter by model |
| `cpu` | str | Filter by CPU (e.g. "Intel i5", "AMD Ryzen 7") |
| `cpu_generation` | str | Filter by CPU generation (e.g. "12th Gen", "Ryzen 7000") |
| `ram` | int | Minimum RAM in GB |
| `storage_min` | int | Minimum storage in GB |
| `storage_max` | int | Maximum storage in GB |
| `storage_type` | str | Storage type (e.g. "SSD", "HDD") |
| `gpu` | str | Filter by GPU |
| `display_size_min` | float | Minimum display size in inches |
| `display_size_max` | float | Maximum display size in inches |
| `condition` | str | Condition (e.g. "Refurbished", "Open Box") |
| `warranty_min` | int | Minimum warranty in months |
| `store_id` | int | Filter by store |
| `price_min` | float | Minimum price |
| `price_max` | float | Maximum price |
| `stock` | str | Filter by stock status ("in_stock", "out_of_stock") |
| `sort` | str | Sort mode (see below) |
| `query` | str | Search query (full-text search across name, brand, model) |

### Sort Modes

| Sort | Description |
|---|---|
| (default) | Created date descending |
| `price_asc` | Price low to high |
| `price_desc` | Price high to low |
| `discount_desc` | Discount high to low |
| `discount_asc` | Discount low to high |
| `name_asc` | Product name A-Z |
| `name_desc` | Product name Z-A |
| `ram_asc` | RAM low to high |
| `ram_desc` | RAM high to low |
| `storage_asc` | Storage low to high |
| `storage_desc` | Storage high to low |
| `display_asc` | Display size low to high |
| `display_desc` | Display size high to low |
| `deal_score_desc` | Deal score high to low (reads DB column, zero per-query overhead) |

### Response

```json
{
  "items": [ProductResponse],
  "total": int,
  "page": int,
  "limit": int
}
```

---

## GET /products/search

Alias for `GET /products` with `query` param. Same parameters and response.

---

## GET /products/{id}

Returns full product detail with store name.

### Response

```json
{
  "id": int,
  "store_id": int,
  "store_name": str,
  "brand": str,
  "model": str,
  "product_name": str,
  "cpu": str,
  "cpu_generation": str,
  "ram_gb": int,
  "storage_gb": int,
  "storage_type": str,
  "gpu": str,
  "display_size": float,
  "display_resolution": str,
  "condition": str,
  "warranty_months": int,
  "price": float,
  "original_price": float,
  "discount": float,
  "currency": str,
  "stock_status": str,
  "deal_score": float,
  "product_url": str,
  "image_url": str,
  "images": [str],
  "first_seen": str,
  "last_seen": str,
  "last_updated": str
}
```

---

## GET /stores

Returns all supported stores with statistics.

---

## GET /stores/{id}

Returns store details and scrape statistics.

---

## GET /history/{product_id}

Returns price and stock history for a product.

### Response

```json
{
  "price_history": [{ "price": float, "timestamp": str }],
  "stock_history": [{ "stock_status": str, "timestamp": str }]
}
```

---

## GET /stats

Returns dashboard aggregates: average price, products tracked, stores, in-stock count, out-of-stock count.

---

## POST /alerts

Create a price/stock alert.

### Body

```json
{
  "brand": str,
  "cpu": str,
  "max_price": float,
  "ram": int,
  "storage": int,
  "gpu": str,
  "notify_stock": bool,
  "notify_price": bool
}
```

---

## DELETE /alerts/{id}

Remove an alert.

---

## GET /alerts

List all alerts for the authenticated user.
