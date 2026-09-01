-- D3 — StockPilot: products with no supplier

-- Technique: Outer join

-- List sku, name for products that don't have a valid supplier on file — either no supplier set, or one that no longer exists in suppliers.



-- users(id, email, hashed_password, role, created_at)
-- categories(id, name, parent_id → categories.id)
-- suppliers(id, name, contact_email)
-- products(id, sku, name, category_id, supplier_id, price_cents, current_stock, reorder_level)
-- stock_movements(id, product_id, delta, reason, created_by → users.id, created_at)
-- orders(id, status, created_by, created_at)
-- order_items(id, order_id, product_id, qty, unit_price_cents)



select
    p.sku,
    p.name
from products p
left join suppliers s on p.supplier_id = s.id
where p.supplier_id is null or s.id is null;

