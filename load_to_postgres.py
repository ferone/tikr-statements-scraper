import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import math

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv('PGDATABASE', 'stockdb'),
        user=os.getenv('PGUSER', 'postgres'),
        password=os.getenv('PGPASSWORD', ''),
        host=os.getenv('PGHOST', 'localhost'),
        port=int(os.getenv('PGPORT', 5432))
    )

def safe_int(val):
    if pd.isna(val) or val is None:
        return None
    try:
        return int(float(val))
    except Exception:
        return None

def safe_str(val):
    if pd.isna(val) or val is None:
        return None
    return str(val)

def load_companies(csv_path, conn):
    df = pd.read_csv(csv_path)
    # Map CSV columns to DB columns, fallback to original columns if yfinance ones are missing
    col_map = {
        'symbol': lambda row: row.get('symbol') or row.get('Symbol'),
        'short_name': lambda row: row.get('shortName') or row.get('Name'),
        'long_name': lambda row: row.get('longName') or row.get('Name'),
        'display_name': lambda row: row.get('displayName') or row.get('Name'),
        'language': lambda row: row.get('language'),
        'region': lambda row: row.get('region'),
        'exchange': lambda row: row.get('exchange') or row.get('Stock Exchange'),
        'full_exchange_name': lambda row: row.get('fullExchangeName') or row.get('Stock Exchange (MIC)'),
        'market': lambda row: row.get('market'),
        'quote_type': lambda row: row.get('quoteType'),
        'type_disp': lambda row: row.get('typeDisp'),
        'exchange_timezone_name': lambda row: row.get('exchangeTimezoneName'),
        'exchange_timezone_short_name': lambda row: row.get('exchangeTimezoneShortName'),
        'gmt_offset_milliseconds': lambda row: safe_int(row.get('gmtOffSetMilliseconds')),
        'market_state': lambda row: row.get('marketState'),
        'message_board_id': lambda row: row.get('messageBoardId'),
        'quote_source_name': lambda row: row.get('quoteSourceName'),
        'triggerable': lambda row: safe_str(row.get('triggerable')),
        'custom_price_alert_confidence': lambda row: safe_str(row.get('customPriceAlertConfidence')),
        'has_pre_post_market_data': lambda row: safe_str(row.get('hasPrePostMarketData')),
        'first_trade_date_milliseconds': lambda row: safe_int(row.get('firstTradeDateMilliseconds')),
        'address1': lambda row: row.get('address1'),
        'city': lambda row: row.get('city'),
        'state': lambda row: row.get('state'),
        'zip': lambda row: row.get('zip'),
        'country': lambda row: row.get('country'),
        'phone': lambda row: row.get('phone'),
        'website': lambda row: row.get('website'),
        'industry': lambda row: row.get('industry'),
        'industry_key': lambda row: row.get('industryKey'),
        'industry_disp': lambda row: row.get('industryDisp'),
        'sector': lambda row: row.get('sector'),
        'sector_key': lambda row: row.get('sectorKey'),
        'sector_disp': lambda row: row.get('sectorDisp'),
        'category': lambda row: row.get('category'),
        'fund_family': lambda row: row.get('fundFamily'),
        'legal_type': lambda row: row.get('legalType'),
        'long_business_summary': lambda row: row.get('longBusinessSummary'),
        'full_time_employees': lambda row: safe_int(row.get('fullTimeEmployees')),
    }
    records = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        record = [col_map[col](row_dict) for col in col_map]
        records.append(tuple(record))
    cols = list(col_map.keys())
    query = f"INSERT INTO companies ({', '.join(cols)}) VALUES %s ON CONFLICT (symbol) DO NOTHING"
    with conn.cursor() as cur:
        execute_values(cur, query, records)
    conn.commit()

def load_financials(csv_path, conn):
    df = pd.read_csv(csv_path)
    cols = ['symbol', 'statement', 'fiscal_year', 'fiscal_period', 'key', 'value', 'currency']
    df = df.where(pd.notnull(df), None)
    tuples = [tuple(x) for x in df[cols].to_numpy()]
    query = f"INSERT INTO financials ({', '.join(cols)}) VALUES %s"
    with conn.cursor() as cur:
        execute_values(cur, query, tuples)
    conn.commit()

def main():
    conn = get_conn()
    load_companies('marketstack_all_tickers_enriched.csv', conn)
    # Uncomment and adjust the next line when you have your financials CSV ready
    # load_financials('your_financials.csv', conn)
    conn.close()

if __name__ == "__main__":
    main() 