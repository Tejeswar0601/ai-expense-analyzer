-- ===================================================
-- Bugfix migration: normalize email casing
-- Run this in MySQL Workbench against expense_analyzer.
--
-- Context: email comparisons were case-sensitive, so
-- "Test@Example.com" and "test@example.com" could register as two
-- separate accounts, and login could fail if the casing didn't
-- exactly match what was used at registration. The application code
-- now always lowercases emails - this migration brings your EXISTING
-- accounts in line with that, so login keeps working for them.
-- ===================================================

USE expense_analyzer;

-- STEP 1: Safety check first. This should return ZERO rows.
-- If it returns any rows, you have two existing accounts that only
-- differ by casing (e.g. "Test@x.com" and "test@x.com") - decide
-- which one to keep/merge before running Step 2, or the UPDATE
-- below will fail on a duplicate-email constraint violation.
SELECT LOWER(email) AS lowercased_email, COUNT(*) AS how_many
FROM users
GROUP BY LOWER(email)
HAVING COUNT(*) > 1;

-- STEP 2: Only run this once Step 1 returns zero rows.
-- UPDATE users SET email = LOWER(email) WHERE id > 0;
