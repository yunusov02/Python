-- D2 — StockPilot: products where current_stock < reorder_level

-- Technique: Filtering

-- List sku, name, current_stock, reorder_level for every product currently below its reorder point, worst shortages first.


-- users(id, email, hashed_password, role, created_at)
-- categories(id, name, parent_id → categories.id) 
-- products(id, sku, name, category_id, supplier_id, price_cents, current_stock, reorder_level)


select
    sku,
    name,
    current_stock,
    reorder_level
from products
where current_stock < reorder_level
order by (reorder_level - current_stock) desc;
