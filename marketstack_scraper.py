import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import os

# URL to scrape
URL = "https://marketstack.com/search"

# Output CSV file
OUTPUT_CSV = "marketstack_all_tickers.csv"

# Start browser (using Firefox)
options = FirefoxOptions()
# options.add_argument("--headless")  # Disabled for debugging
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
driver.get(URL)
wait = WebDriverWait(driver, 30)

# Click the 'Search Stocks' button to load the first table
search_btn = wait.until(EC.element_to_be_clickable((By.ID, 'submit')))
search_btn.click()
wait.until(EC.presence_of_element_located((By.XPATH, '//table//tbody/tr')))
time.sleep(1.0)

# Remove output file if it exists
if os.path.exists(OUTPUT_CSV):
    os.remove(OUTPUT_CSV)

page_num = 1
first_page = True

while True:
    # Wait for at least one row in the table
    wait.until(EC.presence_of_element_located((By.XPATH, '//table//tbody/tr')))
    # Scrape all rows from the current table
    table = driver.find_element(By.XPATH, '//table')
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    rows = tbody.find_elements(By.TAG_NAME, 'tr')
    print(f"[DEBUG] Found {len(rows)} rows on page {page_num}.")
    page_rows = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        if len(cols) == 5:
            page_rows.append({
                'Symbol': cols[0].text.strip(),
                'Name': cols[1].text.strip(),
                'Stock Exchange': cols[2].text.strip(),
                'Stock Exchange (MIC)': cols[3].text.strip(),
                'Country': cols[4].text.strip(),
            })
    # Append to CSV after each page
    df = pd.DataFrame(page_rows)
    if first_page:
        df.to_csv(OUTPUT_CSV, index=False, mode='w', header=True)
        first_page = False
    else:
        df.to_csv(OUTPUT_CSV, index=False, mode='a', header=False)
    print(f"[DEBUG] Appended {len(page_rows)} rows to {OUTPUT_CSV}.")
    # Try to scroll down and click the 'Next' button (only if visible)
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)  # Wait for scroll and button to become visible
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-paginate='next' and not(contains(@style, 'display: none'))]")))
        next_btn.click()
        print(f"[DEBUG] Clicked Next for page {page_num}.")
        page_num += 1
        wait.until(EC.staleness_of(rows[0]))
        wait.until(EC.presence_of_element_located((By.XPATH, '//table//tbody/tr')))
        time.sleep(1.0)
    except Exception:
        print("[DEBUG] No more Next button or could not click. Exiting loop.")
        break

print(f"Done. All rows saved to {OUTPUT_CSV}")
driver.quit() 