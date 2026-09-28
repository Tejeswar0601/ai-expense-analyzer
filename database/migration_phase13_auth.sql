-- ===================================================
-- Phase 13 migration: add multi-user support
-- Run this in MySQL Workbench (or mysql CLI) against
-- your existing expense_analyzer database.
-- ===================================================

USE expense_analyzer;

-- 1. New users table
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Add user_id to expenses (nullable for now, since existing rows
--    predate the concept of users - we'll backfill and lock it down
--    in a moment, after you've registered your first account).
ALTER TABLE expenses ADD COLUMN user_id INT NULL AFTER id;
ALTER TABLE expenses ADD CONSTRAINT fk_expenses_user
    FOREIGN KEY (user_id) REFERENCES users(id);
CREATE INDEX idx_expenses_user ON expenses (user_id);

-- ===================================================
-- STOP HERE. Register your first account through the app,
-- then come back and run the two statements below,
-- replacing 1 with your actual new user's id if different
-- (check with: SELECT id, email FROM users;)
-- ===================================================

-- UPDATE expenses SET user_id = 1 WHERE user_id IS NULL;
-- ALTER TABLE expenses MODIFY user_id INT NOT NULL;
