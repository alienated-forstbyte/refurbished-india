# RefurbHub Development Plan

## Vision

Build the best refurbished laptop search engine for India.

The project should become the equivalent of PCPartPicker, but for refurbished laptops.

The architecture must be modular so adding another store requires writing only one scraper.

---

# Guiding Principles

## Never Hardcode

Every store should implement the same interface.

```python
class StoreScraper(BaseScraper):
    name: str
    rate_limit: float

    async def scrape_all(self) -> list[ProductSchema]
```

Adding a new store should require almost no backend changes.

---

## Normalize Everything

Every scraper produces a different format. Everything should become a common `ProductSchema`:

```
brand | model | cpu | ram | storage | gpu | display | price | stock | warranty | condition
```

No frontend code should care where the data originated.

---

# Phase 1: Project Setup ✅

Backend: FastAPI + SQLAlchemy + Alembic + PostgreSQL
Frontend: Next.js + Tailwind
Infrastructure: Docker Compose

Deliverable: Running application scaffold with health check.

---

# Phase 2: Database Models ✅

- Products
- Stores
- Price History
- Stock History
- Images
- Users
- Alerts
- Notification History
- Scrape Logs

All with proper indexes and SQLAlchemy 2.0 async typing.

---

# Phase 3: REST API ✅

- `GET /products` — Paginated listing with filters
- `GET /products/search` — Full-text search
- `GET /products/{id}` — Product detail
- `GET /stores` / `GET /stores/{id}` — Store info
- `GET /history/{product_id}` — Price + stock history
- `GET /stats` — Dashboard aggregates
- `POST /alerts` / `DELETE /alerts/{id}` — Alert CRUD

---

# Phase 4: Authentication ✅

- Register
- Login
- JWT token
- `get_current_user` dependency

---

# Phase 5: Scheduler + Notifications ✅

- Celery Beat runs every hour
- Celery Worker processes scrapes
- Change detection (price changed, back in stock, new product, removed)
- Notification pipeline wired to user alerts

---

# Phase 6: Scrapers

## Functional ✅

| Store | Type | Status |
|---|---|---|
| Cashify | Custom (RSC push data) | ✅ Complete |
| Reboot Estore | Shopify | ✅ Complete |
| EPW India | Shopify | ✅ Complete |
| e-furbished | Shopify | ✅ Complete |
| EzyRefurb | Shopify | ✅ Complete |
| Lenovo Outlet | Lenovo API | ✅ Complete |

## Stubs (needs implementation)

| Store | Approach |
|---|---|
| Asus Refurbished | httpx + direct URL discovery |
| Dell Outlet | Dell Outlet scraping |
| HP Renew | HP Renew scraping |
| Refurbr | Unknown (check site structure) |
| Amazon Renewed | Amazon product advertising API |

---

# Phase 7: Frontend ✅

- Home page with search + stats + featured products
- Product listing with FilterPanel + TanStack Table (9 filter params, 11 sort modes)
- Product detail with PriceChart + specs + history
- Compare page (side-by-side)
- History page (charts + trends)
- Alerts management UI
- Admin dashboard (scrape logs)
- Deals page (top 50 deals, Hot/Good/Fair/Overpriced badges, compare up to 4)

---

# Phase 8: Extended Filters & Sort ✅

- 9 new filter params: storage_min, storage_max, storage_type, display_size_min, display_size_max, condition, cpu_generation, store_id, warranty_min
- 11 sort modes including discount, ram, storage, display, deal_score
- All implemented both backend (SQLAlchemy) and frontend (FilterPanel + ProductListClient)

---

# Phase 9: Deal Scoring ✅

- `deal_scorer.py` — Median price per RAM group + CPU tier, scores 0–100 (CPU 2x weight)
- `deal_score` column on products table (Alembic migration 002, indexed)
- Celery beat task `refresh_deal_scores` every 30 min
- Sort by `deal_score_desc` (SQL `ORDER BY deal_score DESC NULLS LAST`)
- /deals frontend page with color-coded badges (≥80 Hot, ≥60 Good, ≥40 Fair, <40 Overpriced)

---

# Phase 10: Stock Staleness ✅

- `StockBadge` shows inline verification time: "In Stock · 22h ago"
- 24h staleness threshold → badge turns yellow "May be sold out"
- Applies across ProductCard and /deals page

---

# Phase 11: Frontend Polish (Pending)

- Google / GitHub OAuth login
- Wishlist / saved searches
- User settings page
- Improved mobile responsiveness

---

# Phase 12: Notifications (Backend done, channels pending)

Backend pipeline is wired; actual delivery channels need implementation:
- Telegram bot
- Discord webhook
- Slack webhook
- Email (SMTP)
- Web Push

---

# Phase 13: Analytics (Pending)

- Average discount tracking
- Stock turnover rates
- Price history trends
- Popular brands dashboard
- Average selling price
- ML price predictions (future)

---

# Scraper Architecture

```
BaseScraper
    ↓
├── CashifyScraper      (RSC push data extraction)
├── ShopifyBaseScraper   (/products.json API)
│   ├── RebootScraper
│   ├── EPWIndiaScraper
│   ├── EFurbishedScraper
│   └── EzyRefurbScraper
├── LenovoScraper        (openapi.lenovo.com)
├── AsusScraper          (stub)
├── DellScraper          (stub)
└── HPRefurbScraper      (stub)
```

Each scraper implements `scrape_all() → list[ProductSchema]`.

---

# Scheduler Pipeline

```
Every hour (Celery Beat)
    ↓
Iterate enabled stores in DB
    ↓
Look up scraper class in SCRAPER_MAP
    ↓
Call scraper.scrape_all()
    ↓
Normalize results
    ↓
Upsert products (detect price/stock changes)
    ↓
Generate ChangeEvents
    ↓
Match against user alerts
    ↓
Fire notifications
```

---

# Future Ideas

- **ML Price Predictions** — Predict when prices will fall, estimate fair value
- **Browser Extension** — Highlight tracked products while browsing
- **Public API** — Developers can access product data
- **CLI** — `refurbhub search thinkpad`
- **Mobile App** — Android + iOS

---

# Long-Term Goal

Become the central search engine for refurbished laptops in India.

Users should never need to manually browse multiple refurbished stores again.

One search. One dashboard. Complete historical tracking. Powerful alerts. Simple purchasing decisions.
