import psycopg2
import json

def test_screener_manually():
    """Test the screener logic directly, bypassing the FastAPI endpoint"""
    print("Testing screener logic directly...")
    
    # Database connection
    conn = psycopg2.connect('dbname=stockdb user=postgres host=localhost')
    cursor = conn.cursor()
    
    # Build the query (similar to what's in main.py)
    sector = 'Technology'
    base_query = """
    SELECT c.symbol, c.short_name, c.long_name, c.sector, c.industry, c.market, 
           c.exchange, c.country, c.full_time_employees, 
           f.fiscal_year, f.statement, f.key, f.value 
    FROM companies c 
    LEFT JOIN financials f ON c.symbol = f.symbol
    WHERE c.sector = %s
    LIMIT 10
    """
    
    try:
        cursor.execute(base_query, (sector,))
        rows = []
        for row in cursor.fetchall():
            # Convert to dict
            row_dict = {
                'symbol': row[0],
                'short_name': row[1],
                'long_name': row[2],
                'sector': row[3],
                'industry': row[4],
                'market': row[5],
                'exchange': row[6],
                'country': row[7],
                'full_time_employees': row[8],
                'fiscal_year': row[9],
                'statement': row[10],
                'key': row[11],
                'value': row[12]
            }
            rows.append(row_dict)
            
        print(f"Found {len(rows)} results")
        print(json.dumps(rows[:2], indent=2))
        
    except Exception as e:
        print(f"Error executing query: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_screener_manually() 