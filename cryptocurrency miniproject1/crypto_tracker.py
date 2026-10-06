from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from datetime import datetime


# ==========================================
# 1. START CHROME
# ==========================================

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)


# ==========================================
# 2. OPEN COINGECKO
# ==========================================

print("Opening CoinGecko...")

driver.get(
    "https://www.coingecko.com/en/all-cryptocurrencies"
)

time.sleep(5)

print("CoinGecko opened successfully!")


# ==========================================
# 3. FIND CRYPTOCURRENCY ROWS
# ==========================================

rows = driver.find_elements(
    "xpath",
    "//table//tbody/tr"
)

print("Number of rows found:", len(rows))


# ==========================================
# 4. EXTRACT TOP 10
# ==========================================

crypto_data = []

for i, row in enumerate(rows[:10], start=1):

    try:

        cells = row.find_elements(
            "xpath",
            ".//td"
        )

        if len(cells) >= 9:

            coin = cells[1].text.strip()

            price = cells[2].text.strip()

            change_24h = cells[4].text.strip()

            market_cap = cells[8].text.strip()

            crypto_data.append({

                "Rank": i,

                "Coin": coin,

                "Price": price,

                "24h Change": change_24h,

                "Market Cap": market_cap,

                "Timestamp": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            })

    except Exception as e:

        print("Error:", e)


# ==========================================
# 5. CREATE DATAFRAME
# ==========================================

df = pd.DataFrame(crypto_data)


# ==========================================
# 6. DISPLAY DATA
# ==========================================

print("\n========================================")
print("TOP 10 CRYPTOCURRENCIES")
print("========================================")

print(df.to_string(index=False))


# ==========================================
# 7. SAVE CSV
# ==========================================

df.to_csv(
    "crypto_data.csv",
    index=False
)

print("\n✅ Data saved successfully!")

print("✅ File: crypto_data.csv")


# ==========================================
# 8. CLOSE BROWSER
# ==========================================

input("\nPress Enter to close...")

driver.quit()