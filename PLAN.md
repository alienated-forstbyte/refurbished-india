# RefurbHub Development Plan

## Vision

Build the best refurbished laptop search engine for India.

The project should become the equivalent of PCPartPicker, but for refurbished laptops.

The architecture must be modular so adding another store requires writing only one scraper.

---

# Guiding Principles

## Never Hardcode

Every store should implement the same interface.

```
class StoreScraper:

    name

    async scrape()

    async get_product()

    async normalize()
```

Adding a new store should require almost no backend changes.

---

## Normalize Everything

Every scraper produces a different format.

Everything should become

```
Product

id

brand

model

price

original_price

discount

cpu

ram

storage

gpu

display

condition

availability

warranty

seller

url

images

last_seen
```

No frontend code should care where the data originated.

---

# Phase 1

## Project Setup

Backend

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

Frontend

- Next.js
- Tailwind

Infrastructure

- Docker Compose

Deliverable

Running application.

---

# Phase 2

Database

Create

Products

Stores

Availability History

Price History

Images

Scrape Logs

Users

Saved Searches

Alerts

---

# Phase 3

Lenovo Scraper

Objectives

- Discover every product
- Parse specifications
- Detect stock
- Save images
- Save prices

Challenges

Lenovo uses

- Dynamic pages
- Pagination
- JavaScript

Use Playwright if required.

Deliverable

Database populated from Lenovo.

---

# Phase 4

Asus Scraper

Objectives

Discover

Visible products

Hidden products

Direct URLs

Normalize everything.

---

# Phase 5

Scheduler

Every hour

```
Run Lenovo

Run Asus

Compare

Store Changes

Generate Events
```

Events

Price Changed

Back In Stock

Removed

New Product

---

# Phase 6

REST API

Products

Stores

Statistics

History

Search

Compare

Alerts

Example

GET /products

GET /products/search

GET /history

GET /alerts

GET /stores

---

# Phase 7

Frontend

Pages

Home

Product

Compare

History

Saved Searches

Alerts

Admin

Dashboard widgets

Product cards

Availability

Discount

Charts

Search

---

# Phase 8

Authentication

Google

GitHub

Email

Saved

Alerts

Wishlist

Settings

---

# Phase 9

Notifications

Telegram

Discord

Slack

Email

Push

Examples

ThinkPad available

Price dropped

New listing

---

# Phase 10

Analytics

Average discount

Stock turnover

Price history

Availability graph

Popular brands

Average selling price

---

# Scraper Architecture

```
BaseScraper

↓

LenovoScraper

↓

AsusScraper

↓

DellScraper

↓

HPRefurbScraper
```

Each scraper should implement

```
discover_products()

scrape_product()

normalize()

save()
```

---

# Scheduler

```
Every hour

↓

Fetch URLs

↓

Visit URLs

↓

Extract data

↓

Normalize

↓

Save

↓

Compare

↓

Generate Events

↓

Notify Users
```

---

# Future Ideas

Machine learning

Predict when prices will fall.

Predict stock probability.

Estimate fair value.

---

Browser Extension

Highlight tracked products while browsing.

---

Public API

Developers can access product data.

---

CLI

```
refurbhub search thinkpad

refurbhub alerts

refurbhub compare
```

---

Mobile App

Android

iOS

---

# Long-Term Goal

Become the central search engine for refurbished laptops in India.

Users should never need to manually browse multiple refurbished stores again.

One search.

One dashboard.

Complete historical tracking.

Powerful alerts.

Simple purchasing decisions.