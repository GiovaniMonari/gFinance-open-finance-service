CREATE TABLE IF NOT EXISTS open_finance_connections (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    provider VARCHAR(50) NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    status VARCHAR(30) NOT NULL,

    last_synced_at TIMESTAMP NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_open_finance_connection_provider_external
        UNIQUE (provider, external_id)
);

CREATE INDEX IF NOT EXISTS idx_open_finance_connections_user_id
    ON open_finance_connections(user_id);

CREATE TABLE IF NOT EXISTS open_finance_accounts (
    id UUID PRIMARY KEY,
    connection_id UUID NOT NULL,
    user_id UUID NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    bank_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    balance NUMERIC(15, 2),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_open_finance_account_connection
        FOREIGN KEY (connection_id)
        REFERENCES open_finance_connections(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_open_finance_account_external
        UNIQUE (connection_id, external_id)
);

CREATE INDEX IF NOT EXISTS idx_open_finance_accounts_connection_id
    ON open_finance_accounts(connection_id);

CREATE INDEX IF NOT EXISTS idx_open_finance_accounts_user_id
    ON open_finance_accounts(user_id);

CREATE TABLE IF NOT EXISTS open_finance_transactions (
    id UUID PRIMARY KEY,
    account_id UUID NOT NULL,
    user_id UUID NOT NULL,

    external_id VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL,

    amount NUMERIC(15, 2) NOT NULL,
    description VARCHAR(255) NOT NULL,
    transaction_date DATE NOT NULL,

    type VARCHAR(30) NOT NULL,
    category VARCHAR(100),
    source VARCHAR(50) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_open_finance_transaction_account
        FOREIGN KEY (account_id)
        REFERENCES open_finance_accounts(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_open_finance_transaction_provider_external
        UNIQUE (provider, external_id)
);

CREATE INDEX IF NOT EXISTS idx_open_finance_transactions_account_id
    ON open_finance_transactions(account_id);

CREATE INDEX IF NOT EXISTS idx_open_finance_transactions_user_id
    ON open_finance_transactions(user_id);

CREATE INDEX IF NOT EXISTS idx_open_finance_transactions_date
    ON open_finance_transactions(transaction_date);

CREATE TABLE IF NOT EXISTS open_finance_sync_jobs (
    id UUID PRIMARY KEY,
    connection_id UUID NOT NULL,
    user_id UUID NOT NULL,

    status VARCHAR(30) NOT NULL,

    accounts_count INTEGER NOT NULL DEFAULT 0,
    transactions_count INTEGER NOT NULL DEFAULT 0,

    error TEXT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sync_job_connection
        FOREIGN KEY (connection_id)
        REFERENCES open_finance_connections(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_open_finance_sync_jobs_connection_id
    ON open_finance_sync_jobs(connection_id);

CREATE INDEX IF NOT EXISTS idx_open_finance_sync_jobs_user_id
    ON open_finance_sync_jobs(user_id);

CREATE INDEX IF NOT EXISTS idx_open_finance_sync_jobs_status
    ON open_finance_sync_jobs(status);        