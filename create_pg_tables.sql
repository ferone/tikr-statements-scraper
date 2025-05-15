CREATE TABLE companies (
    symbol TEXT PRIMARY KEY,
    short_name TEXT,
    long_name TEXT,
    display_name TEXT,
    language TEXT,
    region TEXT,
    exchange TEXT,
    full_exchange_name TEXT,
    market TEXT,
    quote_type TEXT,
    type_disp TEXT,
    exchange_timezone_name TEXT,
    exchange_timezone_short_name TEXT,
    gmt_offset_milliseconds BIGINT,
    market_state TEXT,
    message_board_id TEXT,
    quote_source_name TEXT,
    triggerable TEXT,
    custom_price_alert_confidence TEXT,
    has_pre_post_market_data TEXT,
    first_trade_date_milliseconds BIGINT,
    address1 TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    country TEXT,
    phone TEXT,
    website TEXT,
    industry TEXT,
    industry_key TEXT,
    industry_disp TEXT,
    sector TEXT,
    sector_key TEXT,
    sector_disp TEXT,
    category TEXT,
    fund_family TEXT,
    legal_type TEXT,
    long_business_summary TEXT,
    full_time_employees INTEGER
    -- Add more fields as needed from YF_FIELDS
);

DROP TABLE IF EXISTS financials CASCADE;
CREATE TABLE financials (
    id SERIAL PRIMARY KEY,
    symbol TEXT REFERENCES companies(symbol),
    statement TEXT,         -- e.g. 'income_statement', 'cashflow_statement', 'balancesheet_statement'
    fiscal_year INTEGER,
    fiscal_period TEXT,     -- e.g. 'FY', 'Q1', 'Q2', etc. (if you want quarterly granularity)
    key TEXT,               -- e.g. 'Net Income', 'Revenues', etc.
    value DOUBLE PRECISION,
    currency TEXT DEFAULT 'USD',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_financials_symbol_statement_year_key ON financials(symbol, statement, fiscal_year, key);

DROP TABLE IF EXISTS prices CASCADE;
CREATE TABLE prices (
    id SERIAL PRIMARY KEY,
    symbol TEXT REFERENCES companies(symbol),
    date DATE,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume BIGINT,
    adj_close DOUBLE PRECISION
);
CREATE INDEX idx_prices_symbol_date ON prices(symbol, date); 