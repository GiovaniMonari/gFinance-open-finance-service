ALTER TABLE open_finance_connections
ALTER COLUMN user_id TYPE VARCHAR(255);

ALTER TABLE open_finance_accounts
ALTER COLUMN user_id TYPE VARCHAR(255);

ALTER TABLE open_finance_transactions
ALTER COLUMN user_id TYPE VARCHAR(255);

ALTER TABLE open_finance_sync_jobs
ALTER COLUMN user_id TYPE VARCHAR(255);