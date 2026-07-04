# RefurbHub Architecture

## Overview

RefurbHub is designed around a simple principle:

> Every refurbished laptop store is simply another data source.

The rest of the application should never care where the data originated.

---

# High-Level Architecture

                    Scheduler
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
 Lenovo Scraper     Asus Scraper      Dell Scraper
      │                  │                  │
      └──────────────────┼──────────────────┘
                         │
                  Product Normalizer
                         │
                  Change Detection
                         │
                  PostgreSQL Database
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
     REST API      Notification      Analytics
        │
     Next.js Frontend

---

# Components

## Scrapers

Responsibilities

- Discover products
- Visit product pages
- Extract data
- Normalize data
- Report failures

Scrapers NEVER modify database logic.

---

## Normalizer

Converts

Lenovo

↓

Common Product

Asus

↓

Common Product

Dell

↓

Common Product

---

## Database

Stores

Current Product

Historical Prices

Historical Availability

Images

Users

Alerts

Statistics

---

## Scheduler

Runs every hour.

Future support:

- Multiple queues
- Retry failed jobs
- Prioritize stores
- Parallel scraping

---

## API

Only communicates with normalized data.

Never directly accesses scrapers.

---

## Frontend

Communicates only with REST API.

No scraper-specific code.

---

# Design Philosophy

Every component has exactly one responsibility.

Scraper

↓

Normalize

↓

Store

↓

Serve

↓

Display

No shortcuts.

No duplicated logic.
