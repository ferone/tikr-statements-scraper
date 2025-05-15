import pandas as pd
import yfinance as yf
import time
import os
import concurrent.futures

INPUT_CSV = 'marketstack_all_tickers.csv'
OUTPUT_CSV = 'marketstack_all_tickers_enriched.csv'
SLEEP_TIME = 2.0  # seconds between requests to avoid rate limits
MAX_WORKERS = 1   # Single-threaded for maximum safety
BATCH_SIZE = 10

# Explicitly list all yfinance .info fields you want to capture, in your preferred order
YF_FIELDS = [
    # Company Info
    'symbol', 'shortName', 'longName', 'displayName', 'language', 'region', 'exchange', 'fullExchangeName', 'market', 'quoteType', 'typeDisp', 'exchangeTimezoneName', 'exchangeTimezoneShortName', 'gmtOffSetMilliseconds', 'marketState', 'messageBoardId', 'quoteSourceName', 'triggerable', 'customPriceAlertConfidence', 'hasPrePostMarketData', 'firstTradeDateMilliseconds',
    # Address & Contact
    'address1', 'city', 'state', 'zip', 'country', 'phone', 'website',
    # Industry & Sector
    'industry', 'industryKey', 'industryDisp', 'sector', 'sectorKey', 'sectorDisp', 'category', 'fundFamily', 'legalType',
    # Business & Employees
    'longBusinessSummary', 'fullTimeEmployees', 'companyOfficers', 'executiveTeam', 'irWebsite', 'manager',
    # Risk & Governance
    'auditRisk', 'boardRisk', 'compensationRisk', 'shareHolderRightsRisk', 'overallRisk', 'governanceEpochDate', 'compensationAsOfEpochDate', 'maxAge',
    # ESG
    'esgPopulated', 'isEsgPopulated', 'esgScores',
    # Price & Trading
    'priceHint', 'previousClose', 'open', 'dayLow', 'dayHigh', 'regularMarketPreviousClose', 'regularMarketOpen', 'regularMarketDayLow', 'regularMarketDayHigh', 'regularMarketPrice', 'regularMarketChange', 'regularMarketChangePercent', 'regularMarketDayRange', 'regularMarketVolume', 'averageVolume', 'averageVolume10days', 'averageDailyVolume10Day', 'averageDailyVolume3Month', 'bid', 'ask', 'bidSize', 'askSize', 'volume', 'postMarketTime', 'postMarketPrice', 'postMarketChange', 'postMarketChangePercent', 'regularMarketTime',
    # 52 Week & Moving Averages
    'fiftyTwoWeekLow', 'fiftyTwoWeekLowChange', 'fiftyTwoWeekLowChangePercent', 'fiftyTwoWeekHigh', 'fiftyTwoWeekHighChange', 'fiftyTwoWeekHighChangePercent', 'fiftyTwoWeekRange', 'fiftyTwoWeekChange', 'fiftyTwoWeekChangePercent', 'SandP52WeekChange', 'fiftyDayAverage', 'fiftyDayAverageChange', 'fiftyDayAverageChangePercent', 'twoHundredDayAverage', 'twoHundredDayAverageChange', 'twoHundredDayAverageChangePercent', '52WeekChange',
    # Dividend & Split
    'dividendRate', 'dividendYield', 'exDividendDate', 'dividendDate', 'trailingAnnualDividendRate', 'trailingAnnualDividendYield', 'forwardAnnualDividendRate', 'forwardAnnualDividendYield', 'fiveYearAvgDividendYield', 'lastDividendValue', 'lastDividendDate', 'lastSplitFactor', 'lastSplitDate',
    # Valuation
    'marketCap', 'enterpriseValue', 'impliedSharesOutstanding', 'floatShares', 'sharesOutstanding', 'sharesShort', 'sharesShortPriorMonth', 'sharesShortPreviousMonthDate', 'dateShortInterest', 'sharesPercentSharesOut', 'heldPercentInsiders', 'heldPercentInstitutions', 'shortRatio', 'shortPercentOfFloat', 'bookValue', 'priceToBook', 'priceToSalesTrailing12Months', 'enterpriseToRevenue', 'enterpriseToEbitda', 'beta', 'beta3Year', 'totalAssets', 'yield',
    # Earnings & Financials
    'lastFiscalYearEnd', 'nextFiscalYearEnd', 'mostRecentQuarter', 'earningsQuarterlyGrowth', 'netIncomeToCommon', 'trailingEps', 'forwardEps', 'epsTrailingTwelveMonths', 'epsForward', 'epsCurrentYear', 'priceEpsCurrentYear', 'earningsGrowth', 'revenueGrowth', 'grossMargins', 'ebitdaMargins', 'operatingMargins', 'profitMargins', 'returnOnAssets', 'returnOnEquity', 'totalRevenue', 'revenuePerShare', 'totalCash', 'totalCashPerShare', 'ebitda', 'totalDebt', 'debtToEquity', 'freeCashflow', 'operatingCashflow', 'grossProfits', 'financialCurrency', 'annualReportExpenseRatio', 'threeYearAverageReturn', 'fiveYearAverageReturn', 'ytdReturn',
    # Analyst & Target
    'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice', 'recommendationMean', 'recommendationKey', 'numberOfAnalystOpinions', 'averageAnalystRating', 'morningStarOverallRating', 'morningStarRiskRating',
    # Miscellaneous
    'tradeable', 'cryptoTradeable', 'sourceInterval', 'exchangeDataDelayedBy', 'fundInceptionDate', 'pegRatio',
]

# Load the structured tickers
input_df = pd.read_csv(INPUT_CSV)

# If output file exists, load it to skip already enriched rows
if os.path.exists(OUTPUT_CSV):
    enriched_df = pd.read_csv(OUTPUT_CSV)
    enriched_symbols = set(enriched_df['Symbol'])
else:
    enriched_df = pd.DataFrame(columns=input_df.columns)
    enriched_symbols = set()

# Ensure all YF_FIELDS are present in the dataframe efficiently
def add_missing_columns(df, columns):
    missing = [col for col in columns if col not in df.columns]
    if missing:
        missing_df = pd.DataFrame('', index=df.index, columns=missing)
        df = pd.concat([df, missing_df], axis=1)
    return df

input_df = add_missing_columns(input_df, YF_FIELDS)
enriched_df = add_missing_columns(enriched_df, YF_FIELDS)

# Prepare tickers to enrich
rows_to_enrich = []
for i, row in input_df.iterrows():
    ticker = str(row['Symbol']).strip()
    if ticker in enriched_symbols:
        out_row = enriched_df[enriched_df['Symbol'] == ticker].iloc[0]
        if pd.notna(out_row.get('exchange', '')) and out_row.get('exchange', '') != '':
            print(f"{i+1}/{len(input_df)}: {ticker} already enriched, skipping.")
            continue
    rows_to_enrich.append((i, row))

def append_to_csv(df, output_csv, header):
    df.to_csv(output_csv, mode='a', index=False, header=header)

# Parallel yfinance info fetching (now single-threaded, one attempt only)
def get_yf_data(args):
    i, row = args
    ticker = str(row['Symbol']).strip()
    try:
        info = yf.Ticker(ticker).info
        time.sleep(SLEEP_TIME)
        if not info or ('error' in info and info['error']):
            raise Exception(f"Empty or error info for {ticker}")
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        info = {}
    enriched = row.copy()
    for col in YF_FIELDS:
        enriched[col] = info.get(col, '')
    print(f"{i+1}/{len(input_df)}: {ticker} -> {info.get('exchange','')}, {info.get('sector','')}, {info.get('country','')}")
    return enriched

# Write each row immediately after processing
file_exists = os.path.exists(OUTPUT_CSV)
rows_written = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    for enriched in executor.map(get_yf_data, rows_to_enrich):
        batch_df = pd.DataFrame([enriched])
        append_to_csv(batch_df, OUTPUT_CSV, header=not file_exists and rows_written == 0)
        rows_written += 1
        file_exists = True

print(f"Appended {rows_written} new rows to {OUTPUT_CSV}") 