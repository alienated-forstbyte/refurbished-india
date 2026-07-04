# Writing a Scraper

Every scraper follows the same lifecycle.

Discover

↓

Extract

↓

Normalize

↓

Save

Never skip normalization.

---

# Base Interface

Every scraper must implement

discover_products()

fetch_product()

normalize()

save()

---

# discover_products()

Responsible for finding every product URL.

Should return

List[ProductURL]

---

# fetch_product()

Downloads one product page.

Returns raw HTML or JSON.

---

# normalize()

Converts raw page into

NormalizedProduct

Never writes to database.

---

# save()

Persists normalized product.

---

# Error Handling

Network errors

Retry 3 times.

Parsing errors

Log and continue.

Missing fields

Store NULL.

Never crash the scraper.

---

# Logging

Every scraper should log

Pages visited

Products found

Products updated

Products removed

Errors

Duration

---

# Rate Limiting

Respect robots.txt where appropriate.

Maximum

1 request / second

unless site allows more.

Random delays.

Rotate User-Agent.

Support proxies.

---

# Images

Download only URLs.

Do not download image files.

---

# Product Identity

Primary identity

Store

+

Product ID

Fallback

Store

+

Canonical URL

Never identify using title.

Titles change.

---

# Testing

Each scraper must include

Sample HTML

Unit tests

Normalization tests

Regression tests
