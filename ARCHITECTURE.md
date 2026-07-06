# RefurbHub Architecture

## Overview

RefurbHub is designed around a simple principle:

> Every refurbished laptop store is simply another data source.

The rest of the application should never care where the data originated.

---

# High-Level Architecture

```
                    Scheduler (Celery Beat)
                          │
       ┌──────────────────┼──────────────────────┐
       │                  │                      │
  Cashify Scraper    Shopify Scrapers      Lenovo Scraper
  (RSC push data)    (Reboot, EPW,         (openapi.lenovo.com)
                      e-furbished,
                      EzyRefurb)
       │                  │                      │
       └──────────────────┼──────────────────────┘
                          │
                   Product Normalizer
                          │
                    Change Detection
                          │
                         Deal Scorer  ← Celery beat (every 30 min)
                          │
                   PostgreSQL Database
                          │
         ┌────────────────┼─────────────────┬──────────────┐
         │                │                 │              │
      REST API       Notification      Analytics     Deal Scores
         │                                           (DB column)
         │
      Next.js Frontend
         │
    ┌────┴────┐
 Products   Deals (top 50, compare 4)

Remaining stubs: AsusScraper, DellScraper, HPRefurbScraper
```

---

# Components

## Scrapers

Responsibilities:
- Discover products (or scrape all in one pass)
- Visit product pages / call APIs
- Extract data
- Normalize into `ProductSchema`
- Report failures

Scrapers NEVER modify database logic directly. They return `ProductSchema` objects which are saved by the task pipeline.

### Functional Scrapers

| Scraper | Store | Method | Lines |
|---|---|---|---|---|
| `CashifyScraper` | cashify.in | Parse Next.js RSC push payloads | 257 |
| `ShopifyBaseScraper` | Generic Shopify | `/products.json` API with pagination | 360 |
| `RebootScraper` | estore.reboot.co.in | Extends ShopifyBaseScraper | 9 |
| `EPWIndiaScraper` | epwindia.com | Extends ShopifyBaseScraper + laptop filter | 45 |
| `EFurbishedScraper` | e-furbished.in | Extends ShopifyBaseScraper | 9 |
| `EzyRefurbScraper` | ezyrefurb.com | Extends ShopifyBaseScraper | 9 |
| `LenovoScraper` | lenovo.com/outletin | `openapi.lenovo.com` search API + product page specs | 300+ |

**Note**: Stock data from Lenovo's search API can be stale — products shown as "Available" in the API may appear as "Available Soon" on the actual product page. Verification-time badges help users gauge data freshness.

### Stub Scrapers

| Scraper | Store | Notes |
|---|---|---|
| `AsusScraper` | Asus Refurbished | Needs httpx + spec parsing |
| `DellScraper` | Dell Outlet | Needs implementation |
| `HPRefurbScraper` | HP Renew | Needs implementation |

---

## Normalizer

Converts raw `ProductSchema` (from scrapers) into validated, enriched products ready for DB.

Handles:
- Missing fields → NULL
- Field type coercion
- Discount calculation
- CPU generation extraction

---

## Database

Stores:
- Current Product
- Historical Prices
- Historical Availability
- Images
- Users
- Alerts
- Notification History
- Scrape Logs

---

## Scheduler

Celery Beat runs `scrape_all_stores` every hour. The task:
1. Iterates enabled stores in the DB
2. Looks up the scraper class in `SCRAPER_MAP`
3. Calls `scraper.scrape_all()`
4. Normalizes results
5. Upserts products (detects price/stock changes)
6. Generates change events
7. Fires notifications for matched alerts

---

## API

Only communicates with normalized data. Never directly accesses scrapers.

Endpoints under `/api/v1`:
- `GET /products` — Paginated product list with 9 filter params + 11 sort modes (including `deal_score_desc`)
- `GET /products/search` — Full-text + field search
- `GET /products/{id}` — Single product detail (includes `store_name` and `deal_score`)
- `GET /stores` — All stores with stats
- `GET /stores/{id}` — Store details
- `GET /history/{product_id}` — Price + stock history
- `GET /stats` — Dashboard aggregates
- `POST /auth/register` — User registration
- `POST /auth/login` — JWT login
- `GET /alerts` / `POST /alerts` / `DELETE /alerts/{id}` — Alert CRUD

---

## Frontend

Communicates only with REST API. No scraper-specific code.

Pages: Home, Products (table, 9 filters + 11 sort modes), Product Detail (with chart), Compare, Deals (top 50 + compare up to 4), History, Alerts, Admin.

---

# Design Philosophy

Every component has exactly one responsibility.

```
Scraper → Normalize → Store → Serve → Display
```

No shortcuts. No duplicated logic.
