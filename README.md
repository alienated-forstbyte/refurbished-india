# RefurbHub India

> A unified search and monitoring platform for refurbished laptops from OEM and trusted refurbished stores in India.

## Overview

Buying refurbished laptops in India is surprisingly difficult.

Every manufacturer has their own store with different layouts, filtering capabilities, stock indicators, and search functionality.

Some stores, such as Lenovo Refurbished, contain hundreds of products but do not provide an easy way to filter out out-of-stock devices.

Others, like Asus Refurbished, expose only a subset of products while additional products remain accessible through direct URLs.

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

# Supported Stores (Planned)

## OEM Stores

- Lenovo Refurbished
- Asus Refurbished
- Dell Outlet
- HP Renew

## Marketplaces

- Amazon Renewed
- Flipkart Refurbished
- Cashify
- Electronics Bazaar
- Other Indian refurbishers

The architecture should make adding new stores simple.

---

# Features

## Product Aggregation

Every product is normalized into a common format regardless of source.

Example

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

Search by

- ThinkPad
- Legion
- Vivobook
- Latitude
- EliteBook

Supports partial matching.

---

## Filters

### Availability

- In Stock
- Out of Stock

### Price

Minimum and maximum

### Hardware

- CPU Generation
- Intel
- AMD
- RAM
- SSD
- GPU
- Screen Size

### Business

- Warranty
- Grade
- Seller

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

Each product stores

- Price history
- Availability history
- Last checked
- First seen

---

## Alerts

Example

Notify me when

- ThinkPad T14
- Price below ₹55,000
- In Stock

Supported notifications

- Email
- Telegram
- Discord
- Slack
- Web Push

---

## Dashboard

The web interface provides

- Global search
- Filters
- Product comparison
- Availability badges
- Discount badges
- Historical charts

---

# Technology Stack

## Backend

Python

FastAPI

SQLAlchemy

PostgreSQL

Redis

Celery

Playwright

BeautifulSoup

HTTPX

---

## Frontend

Next.js

React

TypeScript

TailwindCSS

TanStack Table

Chart.js

---

## Infrastructure

Docker

Docker Compose

GitHub Actions

PostgreSQL

Redis

Nginx

---

# Project Structure

```
refurbhub/

backend/
    app/
    scrapers/
    api/
    models/
    services/

frontend/

database/

docker/

docs/

scripts/

tests/

README.md

PLAN.md
```

---

# Data Flow

```
Scheduler

↓

Store Scrapers

↓

Normalizer

↓

Database

↓

REST API

↓

Frontend
```

---

# Why This Exists

Current refurbished laptop stores suffer from several problems

- Poor search
- Poor filtering
- Hidden inventory
- No stock monitoring
- No historical pricing
- No cross-store comparison

This project solves all of these.

---

# Current Status

Project is currently in planning.

See PLAN.md for implementation roadmap.