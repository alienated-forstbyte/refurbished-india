# RefurbHub India

> A unified search and monitoring platform for refurbished laptops from OEM and trusted refurbished stores in India.

## Overview

Buying refurbished laptops in India is surprisingly difficult.

Every manufacturer has their own store with different layouts, filtering capabilities, stock indicators, and search functionality.

Some stores contain hundreds of products but do not provide an easy way to filter out out-of-stock devices. Others expose only a subset of products while additional products remain accessible through direct URLs.

The goal of this project is to build a single application that continuously collects product information from multiple refurbished laptop stores and presents it in a clean searchable interface.

Instead of manually checking multiple websites every day, users can search once and monitor products over time.

---

# Goals

- Aggregate refurbished laptop listings from multiple sources.
- Track inventory changes.
- Track price history.
- Provide powerful filtering and sorting.
- Notify users when desired products become available.
- Build a public REST API.
- Eventually support mobile notifications.

---

# Supported Stores

## Functional (scraping live data)

| Store | Type | Products |
|---|---|---|
| Cashify | Custom (RSC push data) | 60+ |
| Reboot Estore | Shopify | ~100 |
| EPW India | Shopify | ~100 |
| e-furbished | Shopify | ~100 |
| EzyRefurb | Shopify | 102 |
| Lenovo Outlet | Lenovo API | 49 |
| **Total** | **6 stores** | **623+** |

## Stubs (need implementation)

| Store | Notes |
|---|---|
| Asus Refurbished | httpx + direct URL discovery |
| Dell Outlet | Dell Outlet scraping |
| HP Renew | HP Renew scraping |
| Refurbr | No scraper exists |
| Amazon Renewed | No scraper exists |
| Flipkart Refurbished | Planned |

The architecture makes adding new stores simple — implement one scraper class, add the store to the DB, and register it in `SCRAPER_MAP`.

---

# Quick Start

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Access:
- **Frontend**: http://localhost:3001
- **API**: http://localhost:8001/api/v1
- **Nginx (combined)**: http://localhost:8080

Seed sample data:
```bash
docker cp scripts/seed_stores.py docker-backend-1:/app/ && docker cp scripts/seed_sample_data.py docker-backend-1:/app/ && docker compose exec backend python seed_stores.py && docker compose exec backend python seed_sample_data.py
```

Trigger scrapers:
```bash
docker compose exec backend python -c "from app.tasks import scrape_all_stores; scrape_all_stores.delay()"
```

---

# Features

## Product Aggregation

Every product is normalized into a common format regardless of source.

- Brand
- Model
- CPU
- RAM
- Storage
- GPU
- Display
- Condition
- Warranty
- Price
- Original Price
- Discount
- Availability

---

## Search

Search by brand, model, CPU, or keywords.

Supports partial matching.

---

## Filters

### Availability
- In Stock / Out of Stock

### Price
- Minimum and maximum

### Hardware
- CPU Generation (Intel / AMD)
- RAM
- SSD
- GPU
- Screen Size

### Business
- Warranty
- Condition
- Store/Seller

---

## Sorting

- Lowest Price
- Highest Price
- Highest Discount
- Recently Added
- Last Seen
- Alphabetical

---

## Product History

Each product stores:
- Price history
- Availability history
- Last checked
- First seen

---

## Alerts

Example: "Notify me when ThinkPad T14 — Price below ₹55,000 — In Stock"

Supported channels:
- Email
- Telegram
- Discord
- Slack
- Web Push (planned)

---

## Dashboard

- Global search
- Filters
- Product comparison
- Availability badges
- Discount badges
- Historical charts

---

# Technology Stack

## Backend
- Python / FastAPI
- SQLAlchemy 2.0 (async) + asyncpg
- PostgreSQL 16
- Redis 7
- Celery
- httpx
- Playwright

## Frontend
- Next.js 14 (App Router)
- React / TypeScript
- TailwindCSS
- TanStack Table
- Chart.js

## Infrastructure
- Docker / Docker Compose
- Nginx reverse proxy
- GitHub Actions CI/CD

---

# Project Structure

```
refurbhub/
  backend/
    app/
      scrapers/     # Store-specific scrapers
      api/          # REST API endpoints
      models/       # SQLAlchemy models
      services/     # Scheduler, normalizer, notifier
    alembic/        # DB migrations
  frontend/
    src/
      app/          # Next.js pages
      components/   # Reusable UI components
      lib/          # API client
  docker/           # Docker Compose + nginx config
  scripts/          # Seed data, DB init
  tests/
```

---

# Data Flow

```
Scheduler (Celery Beat)
    ↓
Store Scrapers (httpx / Shopify API / Playwright)
    ↓
Normalizer (common ProductSchema)
    ↓
Change Detection (diff against DB)
    ↓
Database (PostgreSQL)
    ↓
REST API (FastAPI, async)
    ↓
Frontend (Next.js, client-side fetch)
```

---

# Why This Exists

Current refurbished laptop stores suffer from several problems:
- Poor search
- Poor filtering
- Hidden inventory
- No stock monitoring
- No historical pricing
- No cross-store comparison

This project solves all of these.

---

# Current Status

**Active development.** 6 functional scrapers, 8 stores in DB, 623+ products tracked. Backend API and frontend scaffold are complete. See PROGRESS.md for detailed status.
