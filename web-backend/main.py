from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import os
import psycopg2
import psycopg2.extras
import logging
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'stockdb')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

def get_db_connection():
    """Get a new database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# List of fields for screener
FIELDS = [
    'symbol', 'short_name', 'long_name', 'sector', 'industry', 'market', 'exchange',
    'country', 'full_time_employees', 'market_cap', 'price_to_book', 'pe_ratio',
    'dividend_yield', 'revenue', 'net_income', 'total_assets', 'total_debt', 'ebitda',
    'fiscal_year', 'statement', 'key', 'value'
]

# Map front-end field names to DB column references
FIELD_MAP = {
    'symbol': 'c.symbol',
    'short_name': 'c.short_name',
    'long_name': 'c.long_name',
    'sector': 'c.sector',
    'industry': 'c.industry',
    'market': 'c.market',
    'exchange': 'c.exchange',
    'country': 'c.country',
    'full_time_employees': 'c.full_time_employees',
    'fiscal_year': 'f.fiscal_year',
    'statement': 'f.statement',
    'key': 'f.key',
    'value': 'f.value'
}

class ScreenerFilter(BaseModel):
    field: str
    op: str  # '=', '>', '<', '>=', '<=', 'like', etc.
    value: Any

class ScreenerRequest(BaseModel):
    filters: List[ScreenerFilter]
    limit: Optional[int] = 100
    offset: Optional[int] = 0
    columns: Optional[List[str]] = None

@app.get("/fields")
def get_fields():
    return {"fields": FIELDS}

@app.post("/screener")
def screener(req: ScreenerRequest):
    try:
        # First, get matching companies to avoid duplicates from the financials join
        company_query = """
        SELECT c.symbol, c.short_name, c.long_name, c.sector, c.industry, 
               c.market, c.exchange, c.country, c.full_time_employees 
        FROM companies c
        """
        
        where_clauses = []
        params = []
        
        for f in req.filters:
            # Only use company filters (starting with 'c.')
            if f.field in FIELD_MAP and FIELD_MAP[f.field].startswith('c.'):
                field_reference = FIELD_MAP.get(f.field, f.field)
                
                if f.op.lower() == 'like':
                    where_clauses.append(f"{field_reference} LIKE %s")
                    params.append(f"%{f.value}%")
                else:
                    where_clauses.append(f"{field_reference} {f.op} %s")
                    params.append(f.value)
        
        if where_clauses:
            company_query += " WHERE " + " AND ".join(where_clauses)
        
        company_query += " ORDER BY c.symbol LIMIT %s OFFSET %s"
        params.append(req.limit)
        params.append(req.offset)
        
        logger.info(f"Company query: {company_query}")
        logger.info(f"With params: {params}")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Execute company query
        cur.execute(company_query, params)
        companies = [dict(row) for row in cur.fetchall()]
        
        # For each company, get the most recent financial data (optional)
        results = []
        for company in companies:
            # Add the company info to results
            company_data = {
                'symbol': company['symbol'],
                'short_name': company['short_name'],
                'long_name': company['long_name'],
                'sector': company['sector'],
                'industry': company['industry'],
                'market': company['market'],
                'exchange': company['exchange'],
                'country': company['country'],
                'full_time_employees': company['full_time_employees'],
                'latest_financials': {}
            }
            
            # Get latest financial data for key metrics
            financial_query = """
            SELECT f.fiscal_year, f.statement, f.key, f.value 
            FROM financials f 
            WHERE f.symbol = %s
            AND f.fiscal_year = (SELECT MAX(fiscal_year) FROM financials WHERE symbol = %s)
            """
            
            cur.execute(financial_query, (company['symbol'], company['symbol']))
            financials = cur.fetchall()
            
            # Organize financial data by statement type and key
            for fin in financials:
                if fin['statement'] not in company_data['latest_financials']:
                    company_data['latest_financials'][fin['statement']] = {}
                
                company_data['latest_financials'][fin['statement']][fin['key']] = fin['value']
            
            results.append(company_data)
        
        cur.close()
        conn.close()
        
        return {"results": results}
    except Exception as e:
        logger.error(f"Error in screener endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/company/{symbol}")
def get_company(symbol: str):
    try:
        conn = get_db_connection()
        
        # Get company details
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM companies WHERE symbol = %s", (symbol,))
        company = cur.fetchone()
        
        if not company:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get company financials - grouped by fiscal year and statement type
        cur.execute("""
        SELECT fiscal_year, statement, key, value 
        FROM financials 
        WHERE symbol = %s
        ORDER BY fiscal_year DESC, statement
        """, (symbol,))
        
        all_financials = cur.fetchall()
        
        # Organize financials by year and statement type
        organized_financials = defaultdict(lambda: defaultdict(dict))
        for fin in all_financials:
            organized_financials[fin['fiscal_year']][fin['statement']][fin['key']] = fin['value']
        
        # Convert to a more frontend-friendly format
        financials_list = []
        for year, statements in organized_financials.items():
            for statement_type, entries in statements.items():
                financials_list.append({
                    'fiscal_year': year,
                    'statement': statement_type,
                    'data': entries
                })
        
        company_dict = dict(company)
        
        cur.close()
        conn.close()
        
        return {
            "company": company_dict,
            "financials": financials_list
        }
    except Exception as e:
        logger.error(f"Error in get_company endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 