# RefurbHub India — Progress Log

## Initial Setup (Complete)

- Created project documentation: README.md, PLAN.md, ARCHITECTURE.md, API.md, DATABASE.md, SCRAPER_GUIDE.md
- Initialized Git repo with initial commit containing docs
- Defined full tech stack: FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery, Next.js, TailwindCSS

## Phase 1: Project Skeleton & Backend Foundation

### Backend Core

- `backend/app/__init__.py` — Package marker
- `backend/app/config.py` — Centralized config via pydantic-settings. Loads from env vars with sensible defaults. Connection strings for DB, Redis, Celery broker. CORS origins, scheduler interval, rate limits, etc.
- `backend/app/database.py` — SQLAlchemy async engine + session factory. Uses `asyncpg` for PostgreSQL.
- `backend/requirements.txt` — Pinned all Python dependencies: FastAPI, SQLAlchemy 2.0, Alembic, asyncpg, httpx, playwright, beautifulsoup4, celery, redis, pydantic, pydantic-settings, python-jose, passlib, bcrypt, apscheduler.

### Database Models (SQLAlchemy 2.0, async)

All models use `__tablename__`, `Mapped[]` typing, and `mapped_column()` for modern SQLAlchemy 2.0 style.

| Model | Table | Key Fields | Notes |
|---|---|---|---|
| `Store` | `stores` | name, website, country, enabled, last_scrape, scrape_interval | Stores we scrape from |
| `Product` | `products` | store_id (FK), brand, model, product_name, cpu, cpu_generation, ram_gb, storage_gb, storage_type, gpu, display_size, display_resolution, condition, warranty_months, price, original_price, discount, currency, stock_status, product_url, image_url, first_seen, last_seen, last_updated | Central product table; indexes on price, stock, brand, model, cpu_gen, last_seen |
| `PriceHistory` | `price_history` | product_id (FK), price, timestamp | Tracks price changes over time |
| `StockHistory` | `stock_history` | product_id (FK), stock_status, timestamp | Tracks in-stock / out-of-stock changes |
| `Image` | `images` | product_id (FK), url, position | Product image gallery |
| `User` | `users` | email, password_hash, created_at | Auth users |
| `Alert` | `alerts` | user_id (FK), brand, cpu, max_price, ram, storage, gpu, notify_stock, notify_price, enabled | User-defined alerts |
| `NotificationHistory` | `notification_history` | alert_id (FK), product_id (FK), type, timestamp, status | Sent notifications log |
| `ScrapeLog` | `scrape_logs` | store_id (FK), start_time, end_time, products_found, errors, status, duration_ms | Scraper run audit trail |

Indexes match the DATABASE.md spec exactly — every filtered/queried column gets an index.

### Pydantic Schemas

- `ProductCreate`, `ProductResponse`, `ProductList` — serialization/deserialization for products
- `StoreResponse` — store info for API responses
- `AlertCreate`, `AlertResponse` — alert CRUD
- `StatsResponse` — dashboard statistics aggregate
- All schemas use `from_attributes=True` to work with SQLAlchemy models

### API Endpoints (FastAPI)

Mounted under `/api/v1`:

| Endpoint | Method | Handler | Description |
|---|---|---|---|---|
| `/products` | GET | `list_products` | Paginated product list with filters + sort (9 filter params, 11 sort modes) |
| `/products/search` | GET | `search_products` | Full-text + field search |
| `/products/{id}` | GET | `get_product` | Single product detail |
| `/stores` | GET | `list_stores` | All stores with stats |
| `/stores/{id}` | GET | `get_store` | Store details |
| `/history/{product_id}` | GET | `get_product_history` | Price + stock history |
| `/stats` | GET | `get_stats` | Dashboard aggregates |
| `/alerts` | GET | `list_alerts` | List alerts |
| `/alerts` | POST | `create_alert` | Create alert |
| `/alerts/{id}` | DELETE | `delete_alert` | Remove alert |

**New filter params on `GET /products`**: `storage_min`, `storage_max`, `storage_type`, `display_size_min`, `display_size_max`, `condition`, `cpu_generation`, `store_id`, `warranty_min`.

**New sort modes on `GET /products`**: `discount_desc`, `discount_asc`, `name_desc`, `ram_asc`, `ram_desc`, `storage_asc`, `storage_desc`, `display_asc`, `display_desc`, `deal_score_desc` (reads DB column, zero per-query overhead).

### Scrapers

- `base.py` — Abstract `BaseScraper` with interface: `scrape_all()`, `discover_products()`, `fetch_product()`, `normalize()`, `save()`. Retry logic (3 attempts), error handling, rate limiting (1 req/s), random delays, User-Agent rotation.
- `cashify.py` — Fully functional Cashify scraper. Extracts product data from Next.js RSC push payloads. Parses brand, CPU, RAM, storage, display size from product names. Covers all brand category pages.
- `shopify_base.py` — Base class for Shopify stores. Uses `/products.json` API with pagination. Extracts variants, images, HTML specs. 360 lines. Extended by Reboot, EPW India, e-furbished, EzyRefurb.
- `reboot.py`, `epw.py`, `efurbished.py`, `ezyrefurb.py` — Shopify store scrapers. Minimal (extend `ShopifyBaseScraper` with just `shop_domain`). EPW adds laptop-only filtering.
- `lenovo.py` — Lenovo Outlet India scraper. Uses `openapi.lenovo.com` search API for product discovery (pagination, prices, images). Fetches individual product pages for detailed specs (CPU, RAM, storage, GPU, display, warranty). 49 products scraped from official Lenovo Certified Refurbished outlet.
- `asus.py`, `dell.py`, `hp.py` — Store-specific scrapers (stubs). Each implements the base interface but `discover_products()` returns `[]` and `normalize()` returns `None`. Needs implementation.

### Services

- `normalizer.py` — Takes raw scraper data, validates, enriches, returns `ProductSchema`. Handles missing fields → NULL.
- `scheduler.py` — APScheduler-based orchestrator. Runs every hour. Iterates registered scrapers. Calls scrape → normalize → save → detect changes → generate events.
- `change_detector.py` — Compares new scrape with DB state. Generates events: PRICE_CHANGED, BACK_IN_STOCK, REMOVED, NEW_PRODUCT.
- `notifier.py` — Stub for Telegram/Discord/Slack/Email/Push notification channels. Routes events to user alerts.
- `analytics.py` — Aggregation queries: avg discount, stock turnover, price history stats, popular brands, avg selling price.
- `deal_scorer.py` — Computes median prices per RAM group and CPU tier; scores products 0–100 (CPU weighted 2x vs RAM). Stores scores in DB via `refresh_deal_scores` function. Called by Celery beat every 30 min.

### Main App

- `backend/app/main.py` — FastAPI app factory with lifecycle hooks, CORS middleware, router inclusion, health check endpoint.

### Docker

- `backend/Dockerfile` — Multi-stage Python build with Playwright browsers install
- `frontend/Dockerfile` — Node 20, Next.js standalone output
- `docker/docker-compose.yml` — Full stack: PostgreSQL 16, Redis 7, backend API, Celery worker, Celery beat, frontend, Nginx reverse proxy
- `docker/nginx.conf` — Reverse proxy `/api` → backend, `/` → frontend, static asset caching

### Database Migrations

- `backend/alembic.ini` + `backend/alembic/env.py` — Alembic configuration for async migrations
- Migration 001 — Creates all tables and indexes
- Migration 002 — Adds `deal_score` column to `products` with index

### CI/CD

- `.github/workflows/ci.yml` — GitHub Actions: lint (ruff), typecheck (mypy), test (pytest), build Docker images

### Scripts

- `scripts/init_db.sh` — Create DB if not exists, run migrations, seed stores
- `scripts/seed_stores.py` — Seeds initial store entries (Lenovo, Asus, Dell, HP)

### Frontend (Next.js 14, App Router, TypeScript, Tailwind)

- `src/types/index.ts` — TypeScript interfaces mirroring backend schemas (includes `deal_score`, `store_name`)
- `src/lib/api.ts` — API client with fetch wrapper, typed methods for every endpoint
- `src/components/` — Reusable components: ProductCard, ProductTable, FilterPanel, SearchBar, PriceChart, StockBadge (inline verification time, 24h staleness threshold), DiscountBadge, Navbar (with Deals link), Footer, AlertForm, StatsCards
- `src/app/layout.tsx` — Root layout with Navbar + Footer
- `src/app/page.tsx` — Home page with search, stats, featured products
- `src/app/products/page.tsx` — Full product listing with FilterPanel + ProductTable (TanStack Table)
- `src/app/product/[id]/page.tsx` — Product detail with PriceChart, specs, history
- `src/app/compare/page.tsx` — Side-by-side product comparison
- `src/app/deals/page.tsx` — Top 50 deals by score, Hot/Good/Fair/Overpriced badges, compare mode (up to 4 side-by-side)
- `src/app/history/page.tsx` — Historical charts and trends
- `src/app/alerts/page.tsx` — Alert management UI
- `src/app/admin/page.tsx` — Admin dashboard with scrape logs

## Running the Application

### Option 1: Docker Compose (Recommended)

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

This starts PostgreSQL 16, Redis 7, backend API (FastAPI on :8000), Celery worker + beat, frontend (Next.js on :3000), and Nginx reverse proxy on port 80.

The app is accessible at **http://localhost** (via Nginx).

### Option 2: Backend only (native Python)

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Requires PostgreSQL and Redis running separately.

### Option 3: Both native

```bash
# Terminal 1
cd backend && uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm install && npm run dev
```

## Seed Data

```bash
# Via Docker
docker compose -f docker/docker-compose.yml exec backend python scripts/seed_stores.py

# Native
python scripts/seed_stores.py
```

## Tests

```bash
cd backend
pytest tests/ -v
```

---

## Git History

- `111c8ab` — Initial commit: project documentation (README, PLAN, ARCHITECTURE, API, DATABASE, SCRAPER_GUIDE)
- `6edfc50` — `feat: initial application scaffold` — Full application code (84 files, 3288 lines)

---

## What's Next (Planned Phases)

| Phase | Component | Status |
|---|---|---|---|---|
| 1 | Project setup, backend core, models, API, frontend scaffold | ✅ Complete |
| 2 | Cashify scraper (full implementation, RSC data extraction) | ✅ Complete |
| 3 | Shopify-based scrapers (Reboot Estore, EPW India, e-furbished, EzyRefurb) | ✅ Complete |
| 4 | Scheduler + Celery tasks (hourly beat, change detection, notifications) | ✅ Complete |
| 5 | Authentication (register, login, JWT, get_current_user) | ✅ Complete |
| 6 | Notification pipeline wired into Celery tasks (change detection → user alerts → notify) | ✅ Complete |
| 7 | Lenovo scraper (httpx, openapi.lenovo.com) | ✅ Complete |
| 8 | Extended filter/sort options (9 filter params, 11 sort modes on GET /products) | ✅ Complete |
| 9 | Store name on ProductCard (backend join + frontend display) | ✅ Complete |
| 10 | Deal scoring system (backend service, DB column, Celery beat every 30 min) | ✅ Complete |
| 11 | /deals page with compare mode (top 50 deals, Hot/Good/Fair/Overpriced badges) | ✅ Complete |
| 12 | Stock staleness indicator (inline verification time, 24h threshold → "May be sold out") | ✅ Complete |
| 13 | Lenovo scraper stock accuracy fix (verify product page, not just search API) | ⏳ Pending |
| 14 | Asus scraper (httpx needed) | ⏳ Stub |
| 15 | Dell scraper (Dell Outlet) | ⏳ Stub |
| 16 | HP scraper (HP Renew) | ⏳ Stub |
| 17 | Analytics dashboard, ML price predictions | ⏳ Pending |
| 18 | Google / GitHub OAuth login | ⏳ Pending |
| 19 | Wishlist / saved searches | ⏳ Pending |
| 20 | Notification channels (Telegram, Discord, Slack, Email) | ⏳ Pending |
| 21 | Mobile app / PWA | ⏳ Pending |

---

## Notable Design Decisions

1. **Async everywhere** — Backend uses `async/await` throughout. SQLAlchemy async sessions, httpx async client, async scrapers. No blocking calls.
2. **Scraper interface contract** — Every scraper is a drop-in module. Adding a store = write one class. No backend changes.
3. **No image downloads** — Per SCRAPER_GUIDE.md, we store image URLs only, not the files.
4. **Retry with backoff** — Network errors retry 3 times with exponential backoff. Parsing errors log and continue. Never crash the scraper.
5. **Change detection before save** — Scheduler scrapes, normalizes, then compares with DB. Only writes if something changed. Generates typed events.
6. **Price/stock history append-only** — Never mutate history. Always append new entries. Enables full audit trail.
7. **Frontend zero scraper knowledge** — Frontend talks only to REST API. No scraper-specific code in UI.
8. **Pydantic v2 + SQLAlchemy 2.0** — Modern Python patterns throughout.
9. **Deal scores stored in DB column** — Not computed per-request. Celery beat refreshes every 30 min. Zero per-query overhead for deal_score sorting.
10. **Stock staleness based on last_seen timestamp** — Verification time shown inline (e.g., "In Stock · 22h ago"). Turns yellow "May be sold out" after 24h stale.
11. **page param in URL, not React state** — Prevents stale page number when filters change. Always resets to page 1 on filter change.
