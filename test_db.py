import psycopg2
import sys

try:
    print("Attempting to connect to database...")
    conn = psycopg2.connect('dbname=stockdb user=postgres host=localhost')
    cursor = conn.cursor()
    
    # Check companies table
    cursor.execute('SELECT COUNT(*) FROM companies')
    companies_count = cursor.fetchone()[0]
    print(f"Number of companies in database: {companies_count}")
    
    # Check financials table
    cursor.execute('SELECT COUNT(*) FROM financials')
    financials_count = cursor.fetchone()[0]
    print(f"Number of financial records in database: {financials_count}")
    
    # Get sample data
    if companies_count > 0:
        cursor.execute('SELECT symbol, short_name, sector FROM companies LIMIT 5')
        print("\nSample companies:")
        for row in cursor.fetchall():
            print(f"  {row[0]} - {row[1]} - {row[2]}")
    
    conn.close()
    print("Database connection successful!")
    
except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1) 