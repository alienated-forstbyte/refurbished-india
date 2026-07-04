# REST API

Base URL

/api/v1

---

GET /products

Returns paginated products.

---

GET /products/{id}

Returns full product.

---

GET /products/search

Parameters

query

brand

price_min

price_max

cpu

ram

gpu

stock

sort

page

limit

---

GET /stores

Returns supported stores.

---

GET /stores/{id}

Store statistics.

---

GET /history/{product_id}

Returns

Price history

Stock history

---

GET /stats

Returns

Average price

Products tracked

Stores

In-stock count

Out-of-stock count

---

POST /alerts

Create alert.

---

DELETE /alerts/{id}

Remove alert.

---

GET /alerts

List alerts.
