-- Create Admin and Test User Accounts
-- Run this with: psql -U postgres -d smart_ecommerce_db -f create_accounts.sql

-- First, let's clear any existing admin/test accounts
DELETE FROM admin WHERE username = 'admin';
DELETE FROM users WHERE email = 'test@example.com';

-- Create admin account
-- Password: admin123
-- This is a bcrypt hash of "admin123"
INSERT INTO admin (username, password_hash, email, full_name, is_super_admin)
VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqKe.Vu8gy',
    'admin@example.com',
    'System Administrator',
    true
);

-- Create test user account  
-- Password: password123
-- This is a bcrypt hash of "password123"
INSERT INTO users (full_name, email, password_hash, phone, is_active)
VALUES (
    'Test User',
    'test@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqKe.Vu8gy',
    '1234567890',
    true
);

-- Verify accounts created
SELECT 'Admin account:' as type, username, email FROM admin WHERE username = 'admin'
UNION ALL
SELECT 'User account:', email as username, full_name FROM users WHERE email = 'test@example.com';

-- Show success message
\echo ''
\echo '✓ Accounts created successfully!'
\echo ''
\echo 'Admin Login:'
\echo '  Username: admin'
\echo '  Password: admin123'
\echo ''
\echo 'User Login:'
\echo '  Email: test@example.com'
\echo '  Password: password123'
\echo ''
