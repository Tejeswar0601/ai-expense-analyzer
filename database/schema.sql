-- ===================================================
-- AI Expense Analyzer - Database Schema
-- ===================================================

CREATE DATABASE IF NOT EXISTS expense_analyzer;

USE expense_analyzer;

CREATE TABLE IF NOT EXISTS expenses (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    expense_date     DATE NOT NULL,
    amount           DECIMAL(10,2) NOT NULL,
    category         VARCHAR(50) NOT NULL,
    custom_category  VARCHAR(100) NULL,
    note             TEXT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Helpful indexes for common queries (filtering by date/category)
CREATE INDEX idx_expense_date ON expenses (expense_date);
CREATE INDEX idx_category ON expenses (category);
