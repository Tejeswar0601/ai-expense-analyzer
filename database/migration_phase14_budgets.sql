-- ===================================================
-- Phase 14 migration: budgets per category per month
-- Run this in MySQL Workbench against expense_analyzer.
-- ===================================================

USE expense_analyzer;

CREATE TABLE IF NOT EXISTS budgets (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    category       VARCHAR(50) NOT NULL,
    monthly_limit  DECIMAL(10,2) NOT NULL,
    month_year     VARCHAR(7) NOT NULL,  -- format: 'YYYY-MM'
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY uq_budget_user_category_month (user_id, category, month_year)
);
