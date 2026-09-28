-- ===================================================
-- Phase 22 migration: email verification via OTP
-- Run this in MySQL Workbench against expense_analyzer.
-- ===================================================

USE expense_analyzer;

ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN otp_code VARCHAR(6) NULL;
ALTER TABLE users ADD COLUMN otp_expires_at TIMESTAMP NULL;

-- Your existing account(s) predate this feature - mark them verified
-- so you're not nagged for accounts you already trust. New
-- registrations from here on will start as unverified.
UPDATE users SET is_verified = TRUE;
