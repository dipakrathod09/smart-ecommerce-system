-- ===================================================================
-- SMART E-COMMERCE SYSTEM - DATABASE SCHEMA
-- Database: PostgreSQL
-- ===================================================================

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS cart CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS admin CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS wishlists CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;

-- ===================================================================
-- TABLE 1: USERS
-- Purpose: Store customer account information
-- ===================================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hashed password
    phone VARCHAR(15),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    pincode VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP
);

-- Index for faster email lookups during login
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- ===================================================================
-- TABLE 2: ADMIN
-- Purpose: Store admin account information (separate from users)
-- ===================================================================
CREATE TABLE admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hashed password
    email VARCHAR(150) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_super_admin BOOLEAN DEFAULT FALSE
);

-- Index for admin username lookup
CREATE INDEX idx_admin_username ON admin(username);

-- ===================================================================
-- TABLE 3: CATEGORIES
-- Purpose: Product categories for organization
-- ===================================================================
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for category name search
CREATE INDEX idx_categories_name ON categories(name);
CREATE INDEX idx_categories_active ON categories(is_active);

-- ===================================================================
-- TABLE 4: PRODUCTS
-- Purpose: Product catalog with inventory tracking
-- ===================================================================
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    image_url VARCHAR(255),
    brand VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key relationship
    CONSTRAINT fk_product_category 
        FOREIGN KEY (category_id) 
        REFERENCES categories(id) 
        ON DELETE RESTRICT  -- Prevent deleting category if products exist
        ON UPDATE CASCADE
);

-- Indexes for faster product queries
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_products_stock ON products(stock);  -- For inventory alerts

-- ===================================================================
-- TABLE 5: CART
-- Purpose: Shopping cart for users (session-based persistence)
-- ===================================================================
CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key relationships
    CONSTRAINT fk_cart_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,  -- Delete cart items when user is deleted
    
    CONSTRAINT fk_cart_product 
        FOREIGN KEY (product_id) 
        REFERENCES products(id) 
        ON DELETE CASCADE,  -- Delete cart items when product is deleted
    
    -- Ensure user can't add same product twice (update quantity instead)
    CONSTRAINT unique_user_product 
        UNIQUE (user_id, product_id)
);

-- Indexes for cart queries
CREATE INDEX idx_cart_user ON cart(user_id);
CREATE INDEX idx_cart_product ON cart(product_id);

-- ===================================================================
-- TABLE 6: ORDERS
-- Purpose: Order header information
-- ===================================================================
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,  -- e.g., ORD20250201001
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    order_status VARCHAR(50) DEFAULT 'Pending',  
    -- Status: Pending, Confirmed, Processing, Shipped, Delivered, Cancelled
    
    shipping_address TEXT NOT NULL,
    shipping_city VARCHAR(50) NOT NULL,
    shipping_state VARCHAR(50) NOT NULL,
    shipping_pincode VARCHAR(10) NOT NULL,
    contact_phone VARCHAR(15) NOT NULL,
    
    -- Cancellation tracking
    cancel_reason TEXT,
    cancelled_at TIMESTAMP,
    
    -- Return tracking
    return_reason TEXT,
    returned_at TIMESTAMP,
    
    ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key relationship
    CONSTRAINT fk_order_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE RESTRICT  -- Don't delete user if orders exist
        ON UPDATE CASCADE
);

-- Indexes for order queries
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_number ON orders(order_number);
CREATE INDEX idx_orders_date ON orders(ordered_at);

-- ===================================================================
-- TABLE 7: ORDER_ITEMS
-- Purpose: Individual items in each order (order line items)
-- ===================================================================
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(200) NOT NULL,  -- Store name at time of order
    product_price DECIMAL(10, 2) NOT NULL,  -- Store price at time of order
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    subtotal DECIMAL(10, 2) NOT NULL,  -- quantity * product_price
    
    -- Foreign key relationships
    CONSTRAINT fk_orderitem_order 
        FOREIGN KEY (order_id) 
        REFERENCES orders(id) 
        ON DELETE CASCADE,  -- Delete items when order is deleted
    
    CONSTRAINT fk_orderitem_product 
        FOREIGN KEY (product_id) 
        REFERENCES products(id) 
        ON DELETE RESTRICT  -- Keep order history even if product deleted
);

-- Indexes for order item queries
CREATE INDEX idx_orderitems_order ON order_items(order_id);
CREATE INDEX idx_orderitems_product ON order_items(product_id);

-- ===================================================================
-- TABLE 8: PAYMENTS
-- Purpose: Payment transaction records (simulated)
-- ===================================================================
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL UNIQUE,  -- One payment per order
    transaction_id VARCHAR(100) UNIQUE NOT NULL,  -- e.g., TXN20250201123456
    payment_method VARCHAR(50) NOT NULL,  -- COD, Card, UPI
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    payment_status VARCHAR(50) DEFAULT 'Pending',  
    -- Status: Pending, Success, Failed, Refunded
    
    card_last_four VARCHAR(4),  -- For card payments (optional)
    upi_id VARCHAR(100),  -- For UPI payments (optional)
    
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key relationship
    CONSTRAINT fk_payment_order 
        FOREIGN KEY (order_id) 
        REFERENCES orders(id) 
        ON DELETE RESTRICT  -- Keep payment record even if order deleted
);

-- Indexes for payment queries
CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_payments_transaction ON payments(transaction_id);
CREATE INDEX idx_payments_status ON payments(payment_status);
CREATE INDEX idx_payments_method ON payments(payment_method);
CREATE INDEX idx_payments_date ON payments(payment_date);

-- ===================================================================
-- TABLE 9: WISHLISTS
-- Purpose: Store user favorite products
-- ===================================================================
CREATE TABLE wishlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key relationships
    CONSTRAINT fk_wishlist_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_wishlist_product 
        FOREIGN KEY (product_id) 
        REFERENCES products(id) 
        ON DELETE CASCADE,
    
    -- Prevent duplicate wishlist items
    CONSTRAINT unique_user_wishlist_product 
        UNIQUE (user_id, product_id)
);

-- Index for wishlist queries
CREATE INDEX idx_wishlists_user ON wishlists(user_id);

-- ===================================================================
-- TABLE 10: REVIEWS
-- Purpose: Store product ratings and comments
-- ===================================================================
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key relationships
    CONSTRAINT fk_review_product 
        FOREIGN KEY (product_id) 
        REFERENCES products(id) 
        ON DELETE CASCADE,
        
    CONSTRAINT fk_review_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
        
    -- Ensure one review per user per product
    CONSTRAINT unique_user_product_review 
        UNIQUE (user_id, product_id)
);

-- Indexes for review queries
CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);

-- ===================================================================
-- INSERT INITIAL DATA
-- ===================================================================

-- Insert sample categories
INSERT INTO categories (name, description, is_active) VALUES
('Electronics', 'Electronic gadgets and devices', TRUE),
('Clothing', 'Men and women fashion wear', TRUE),
('Books', 'Books and educational materials', TRUE),
('Home & Kitchen', 'Home appliances and kitchen items', TRUE),
('Sports', 'Sports equipment and accessories', TRUE),
('Beauty', 'Beauty and personal care products', TRUE),
('Toys', 'Toys and games for kids', TRUE),
('Groceries', 'Daily essentials and food items', TRUE);

-- Insert sample products (10 products for demonstration)
INSERT INTO products (category_id, name, description, price, stock, brand, is_active) VALUES
-- Electronics
(1, 'Wireless Bluetooth Headphones', 'Premium sound quality with noise cancellation', 2499.00, 50, 'SoundMax', TRUE),
(1, 'Smartphone 128GB', '6.5 inch display, 48MP camera, 5000mAh battery', 15999.00, 30, 'TechPro', TRUE),
(1, 'Smart Watch Fitness Tracker', 'Heart rate monitor, sleep tracking, waterproof', 3499.00, 40, 'FitGear', TRUE),

-- Clothing
(2, 'Men Cotton T-Shirt', 'Comfortable round neck casual wear', 499.00, 100, 'StyleHub', TRUE),
(2, 'Women Denim Jeans', 'Slim fit, stretchable fabric', 1299.00, 60, 'Fashionista', TRUE),

-- Books
(3, 'Python Programming Complete Guide', 'From basics to advanced concepts', 599.00, 80, 'TechBooks', TRUE),
(3, 'Data Structures and Algorithms', 'Comprehensive problem-solving guide', 749.00, 50, 'CodeMaster', TRUE),

-- Home & Kitchen
(4, 'Non-Stick Cookware Set', '5-piece aluminum cookware set', 2999.00, 25, 'KitchenPro', TRUE),
(4, 'Electric Kettle 1.5L', 'Fast boiling, auto shut-off', 899.00, 45, 'HomeEssentials', TRUE),

-- Sports
(5, 'Yoga Mat Premium Quality', 'Anti-slip, eco-friendly, 6mm thick', 799.00, 70, 'FitZone', TRUE);

-- ===================================================================
-- VIEWS FOR COMMON QUERIES (Optional but useful)
-- ===================================================================

-- View: Product details with category name
CREATE OR REPLACE VIEW v_product_details AS
SELECT 
    p.id,
    p.name,
    p.description,
    p.price,
    p.stock,
    p.brand,
    p.image_url,
    p.is_active,
    c.name AS category_name,
    c.id AS category_id
FROM products p
INNER JOIN categories c ON p.category_id = c.id;

-- View: Order summary with user details
CREATE OR REPLACE VIEW v_order_summary AS
SELECT 
    o.id,
    o.order_number,
    o.total_amount,
    o.order_status,
    o.ordered_at,
    u.full_name AS customer_name,
    u.email AS customer_email,
    u.phone AS customer_phone,
    p.payment_method,
    p.payment_status
FROM orders o
INNER JOIN users u ON o.user_id = u.id
LEFT JOIN payments p ON o.id = p.order_id;

-- ===================================================================
-- FUNCTIONS FOR COMMON OPERATIONS
-- ===================================================================

-- Function: Generate unique order number
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    order_num VARCHAR(50);
    counter INTEGER;
BEGIN
    -- Get count of orders today
    SELECT COUNT(*) INTO counter 
    FROM orders 
    WHERE DATE(ordered_at) = CURRENT_DATE;
    
    -- Format: ORD20250201001
    order_num := 'ORD' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || LPAD((counter + 1)::TEXT, 3, '0');
    
    RETURN order_num;
END;
$$ LANGUAGE plpgsql;

-- Function: Generate unique transaction ID
CREATE OR REPLACE FUNCTION generate_transaction_id()
RETURNS VARCHAR(100) AS $$
DECLARE
    txn_id VARCHAR(100);
BEGIN
    -- Format: TXN20250201123456789
    txn_id := 'TXN' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISSMS');
    
    RETURN txn_id;
END;
$$ LANGUAGE plpgsql;

-- ===================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ===================================================================

-- Trigger: Update product stock after order is placed
CREATE OR REPLACE FUNCTION update_product_stock()
RETURNS TRIGGER AS $$
BEGIN
    -- Decrease stock when order item is created
    UPDATE products 
    SET stock = stock - NEW.quantity 
    WHERE id = NEW.product_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_stock
AFTER INSERT ON order_items
FOR EACH ROW
EXECUTE FUNCTION update_product_stock();

-- Trigger: Update timestamps on row modification
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_products_timestamp
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_categories_timestamp
BEFORE UPDATE ON categories
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_orders_timestamp
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- ===================================================================
-- ANALYTICS QUERIES (For reference - used in analytics.py)
-- ===================================================================

-- Total sales revenue
-- SELECT SUM(total_amount) as total_revenue FROM orders WHERE order_status != 'Cancelled';

-- Daily sales for last 30 days
-- SELECT DATE(ordered_at) as sale_date, COUNT(*) as order_count, SUM(total_amount) as revenue
-- FROM orders WHERE ordered_at >= CURRENT_DATE - INTERVAL '30 days'
-- GROUP BY DATE(ordered_at) ORDER BY sale_date;

-- Best selling products
-- SELECT p.name, COUNT(oi.id) as times_sold, SUM(oi.quantity) as total_quantity
-- FROM order_items oi JOIN products p ON oi.product_id = p.id
-- GROUP BY p.id, p.name ORDER BY times_sold DESC LIMIT 10;

-- Low stock alert
-- SELECT id, name, stock, category_id FROM products WHERE stock < 10 AND is_active = TRUE;

-- Category wise sales
-- SELECT c.name, COUNT(oi.id) as items_sold, SUM(oi.subtotal) as revenue
-- FROM order_items oi 
-- JOIN products p ON oi.product_id = p.id
-- JOIN categories c ON p.category_id = c.id
-- GROUP BY c.id, c.name ORDER BY revenue DESC;

-- ===================================================================
-- END OF SCHEMA
-- ===================================================================

-- Grant necessary permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
