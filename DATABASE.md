# Database Design

Database

PostgreSQL

---

# Products

Stores current product information.

Columns

id

store_id

brand

model

product_name

cpu

cpu_generation

ram_gb

storage_gb

storage_type

gpu

display_size

display_resolution

condition

warranty_months

price

original_price

discount

currency

stock_status

product_url

image_url

first_seen

last_seen

last_updated

---

# Stores

id

name

website

country

enabled

last_scrape

scrape_interval

---

# Price History

id

product_id

price

timestamp

---

# Stock History

id

product_id

stock_status

timestamp

---

# Images

id

product_id

url

position

---

# Users

id

email

password_hash

created_at

---

# Alerts

id

user_id

brand

cpu

max_price

ram

storage

gpu

notify_stock

notify_price

enabled

---

# Notification History

id

alert_id

product_id

type

timestamp

status

---

# Scrape Logs

id

store_id

start_time

end_time

products_found

errors

status

duration_ms

---

# Indexes

Products

(price)

(stock_status)

(brand)

(model)

(cpu_generation)

(last_seen)

Price History

(product_id)

(timestamp)

Stock History

(product_id)

(timestamp)

Alerts

(user_id)

(enabled)
