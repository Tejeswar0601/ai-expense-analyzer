-- ===================================================
-- Phase 17 migration: persist AI-generated insights
-- Run this in MySQL Workbench against expense_analyzer.
-- ===================================================

USE expense_analyzer;

CREATE TABLE IF NOT EXISTS ai_insights (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT NOT NULL,
    month_year        VARCHAR(7) NOT NULL,   -- format: 'YYYY-MM'
    insight_type      VARCHAR(50) NOT NULL,  -- 'spending_summary', 'spending_patterns',
                                              -- 'main_expense_categories', 'monthly_summary',
                                              -- or 'recommendation' (one row per recommendation)
    message           TEXT NOT NULL,
    confidence_score  DECIMAL(4,2) NULL,     -- derived from transaction count, not AI-reported
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_ai_insights_user_month ON ai_insights (user_id, month_year);
