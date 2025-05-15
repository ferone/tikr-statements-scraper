import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# URL of the FirstRate Data tickers page
URL = "https://firstratedata.com/b/22/stock-complete-historical-intraday"

# Type inference rules (can be expanded)
def infer_type(symbol, name):
    symbol = symbol.upper()
    if '-DELISTED' in symbol:
        return 'Delisted'
    # Add more rules for ETF, Index, Crypto, Futures if needed
    # Example: if symbol in known_etf_list: return 'ETF'
    return 'Stock'  # Default

def scrape_tickers():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    tickers = []
    for line in soup.text.split('\n'):
        # Regex to match: SYMBOL (Name) Start Date:YYYY-MM-DD
        match = re.match(r"^([A-Z0-9\.\-\_]+)(?: \((.*?)\))? Start Date:([0-9\-]+)", line)
        if match:
            symbol, name, start_date = match.groups()
            ttype = infer_type(symbol, name)
            tickers.append({
                'TikrSymbol': symbol.replace('-DELISTED', ''),
                'Name': name or '',
                'Start Date': start_date,
                'Type': ttype
            })
    return tickers

def main():
    print("Scraping tickers from FirstRate Data...")
    tickers = scrape_tickers()
    df = pd.DataFrame(tickers)
    output_file = 'all_tickers_firstratedata.csv'
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} tickers to {output_file}")

if __name__ == "__main__":
    main() 