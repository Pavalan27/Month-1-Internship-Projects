import argparse
import json
import os
import re
import sys
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def build_chrome_driver(headless: bool = True):
    """Configures and initializes a Chrome WebDriver with anti-bot detection evasion."""
    options = webdriver.ChromeOptions()
    
    if headless:
        options.add_argument("--headless=new")
    else:
        options.add_argument("--start-maximized")

    # Anti-bot detection flags
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    )
    options.add_argument("accept-language=en-US,en;q=0.9")
    
    # Exclude automation switches
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    # Hide webdriver flag via CDP
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
        )
    except Exception:
        pass

    return driver


def scrape_imdb_top_250(output_file: str = "movies.csv", headless: bool = True, max_movies: int = 250):
    """Scrapes IMDb Top 250 movies and saves to CSV."""
    url = "https://www.imdb.com/chart/top/"
    print("=" * 50)
    print("[IMDb Top 250 Scraper]")
    print("=" * 50)
    print(f"Launching Chrome (headless={headless})...")

    driver = build_chrome_driver(headless=headless)
    movies = []

    try:
        print(f"Navigating to {url}...")
        driver.get(url)
        time.sleep(4)

        # Check for Human Verification or 403
        title = driver.title
        print(f"Page Title: {title}")

        if "403 Forbidden" in title:
            print("\n[WARNING] IMDb returned 403 Forbidden with headless mode. Retrying with non-headless mode...")
            driver.quit()
            driver = build_chrome_driver(headless=False)
            driver.get(url)
            time.sleep(5)
            title = driver.title
            print(f"Page Title after retry: {title}")

        if "Human Verification" in title or "Robot Check" in title:
            print("\nIMDb displayed a Human Verification page.")
            if headless:
                print("Headless mode encountered verification. Switching to visible browser...")
                driver.quit()
                driver = build_chrome_driver(headless=False)
                driver.get(url)
            print("Please complete verification in the Chrome window.")
            input("After completing it, press ENTER here to continue...")
            time.sleep(3)

        # Scroll page down progressively to trigger lazy-loaded items (up to 250)
        print("Scrolling page to load all 250 items...")
        for _ in range(6):
            driver.execute_script("window.scrollBy(0, 3500);")
            time.sleep(0.6)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)

        # 1. Parse JSON-LD structured data if available for high-fidelity attributes
        json_ld_map = {}
        try:
            matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', driver.page_source, re.DOTALL)
            for m in matches:
                try:
                    data = json.loads(m)
                    if data.get("@type") == "ItemList":
                        items = data.get("itemListElement", [])
                        for item_wrapper in items:
                            m_item = item_wrapper.get("item", {})
                            name = m_item.get("name")
                            url_val = m_item.get("url", "")
                            
                            # Extract IMDb tt id e.g. tt0111161
                            tt_match = re.search(r'(tt\d+)', url_val)
                            tt_id = tt_match.group(1) if tt_match else ""
                            
                            rating_val = None
                            rating_cnt = None
                            if "aggregateRating" in m_item:
                                rating_val = m_item["aggregateRating"].get("ratingValue")
                                rating_cnt = m_item["aggregateRating"].get("ratingCount")
                                
                            info = {
                                "title": name,
                                "rating": float(rating_val) if rating_val is not None else None,
                                "rating_count": int(rating_cnt) if rating_cnt is not None else None,
                                "genre": m_item.get("genre"),
                                "url": url_val,
                                "image": m_item.get("image"),
                                "description": m_item.get("description")
                            }
                            if tt_id:
                                json_ld_map[tt_id] = info
                            if name:
                                json_ld_map[name.lower().strip()] = info
                except Exception:
                    continue
            if json_ld_map:
                print(f"Extracted metadata for {len(json_ld_map)} items from JSON-LD")
        except Exception as e:
            print(f"Notice: JSON-LD extraction skipped: {e}")

        # 2. Extract movie rows from DOM
        rows = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
        print(f"Found {len(rows)} movie rows in DOM")

        if not rows and json_ld_map:
            print("DOM rows empty, falling back directly to JSON-LD items...")
            # Fallback to JSON-LD items if DOM changes completely
            for idx, (k, info) in enumerate(json_ld_map.items(), start=1):
                if not k.startswith("tt"):
                    continue
                movies.append({
                    "Rank": idx,
                    "Title": info.get("title", f"Movie {idx}"),
                    "Year": "N/A",
                    "Rating": info.get("rating", "N/A"),
                    "Duration": "N/A",
                    "Certificate": "N/A",
                    "Genre": info.get("genre", "N/A"),
                    "Rating_Count": info.get("rating_count", "N/A")
                })
                if len(movies) >= max_movies:
                    break

        for index, row in enumerate(rows[:max_movies], start=1):
            try:
                # --- Title ---
                title = ""
                title_elements = row.find_elements(By.CSS_SELECTOR, "h4.ipc-title__text, h3, .ipc-title__text")
                for te in title_elements:
                    raw_text = te.text.strip()
                    if raw_text:
                        # Clean leading rank if attached e.g. "1. The Shawshank Redemption"
                        clean_title = re.sub(r'^\d+\.\s*', '', raw_text)
                        title = clean_title
                        break

                # --- IMDb Title ID & URL ---
                tt_id = ""
                imdb_url = ""
                link_elements = row.find_elements(By.CSS_SELECTOR, "a[href*='/title/tt']")
                for link in link_elements:
                    href = link.get_attribute("href") or ""
                    match_tt = re.search(r'(tt\d+)', href)
                    if match_tt:
                        tt_id = match_tt.group(1)
                        imdb_url = f"https://www.imdb.com/title/{tt_id}/"
                        break

                # --- Metadata: Year, Duration, Certificate ---
                year = None
                duration = None
                cert = None

                meta_spans = row.find_elements(
                    By.CSS_SELECTOR,
                    ".cli-title-metadata li, span.cli-title-metadata-item, .cli-title-metadata span"
                )
                for item in [s.text.strip() for s in meta_spans if s.text.strip()]:
                    # Match Year (4 digits, e.g. 1994)
                    if re.match(r'^(19\d\d|20\d\d)$', item):
                        year = int(item)
                    # Match Duration (e.g. 2h 22m, 1h 45m, 45m)
                    elif re.search(r'\b\d+\s*h|\b\d+\s*m\b', item):
                        duration = item
                    # Match Age / Content Certificate
                    elif item in ['R', 'PG-13', 'PG', 'G', 'NC-17', 'Approved', 'Passed', 'Not Rated', 'Unrated', 'TV-MA', '16+', '18+', '12+', 'U', 'A', 'U/A']:
                        cert = item

                # Regex fallback for year from entire row text
                if not year:
                    ym = re.search(r'\b(19\d{2}|20\d{2})\b', row.text)
                    if ym:
                        year = int(ym.group(1))

                # --- Rating ---
                rating = None
                rating_elements = row.find_elements(
                    By.CSS_SELECTOR,
                    "span.ipc-rating-star--rating, span.ipc-rating-star, [data-testid='ratingGroup--imdb-rating']"
                )
                for re_elem in rating_elements:
                    m_rate = re.search(r'(\d+\.\d+)', re_elem.text)
                    if m_rate:
                        rating = float(m_rate.group(1))
                        break

                # --- Enrich with JSON-LD data ---
                j_info = json_ld_map.get(tt_id, {}) or json_ld_map.get(title.lower().strip(), {})
                if not title and j_info.get("title"):
                    title = j_info["title"]
                if rating is None and j_info.get("rating") is not None:
                    rating = j_info["rating"]

                genre = j_info.get("genre") or "N/A"
                rating_count = j_info.get("rating_count")
                if not imdb_url and j_info.get("url"):
                    imdb_url = j_info["url"]

                movie = {
                    "Rank": index,
                    "Title": title or f"Movie #{index}",
                    "Year": year if year else "N/A",
                    "Rating": rating if rating is not None else "N/A",
                    "Duration": duration if duration else "N/A",
                    "Certificate": cert if cert else "N/A",
                    "Genre": genre,
                    "Rating_Count": rating_count if rating_count else "N/A"
                }

                movies.append(movie)
                print(f"{index:3d}. {movie['Title']} ({movie['Year']}) - Rating: {movie['Rating']}")

            except Exception as err:
                print(f"[Warning] Could not extract row {index}: {err}")

    finally:
        driver.quit()

    # --- Save Data ---
    if not movies:
        print("\n[ERROR] No movie data was collected.")
        print("IMDb may have displayed Human Verification or blocked the request.")
        return False

    df = pd.DataFrame(movies)
    df.to_csv(output_file, index=False)

    print("\n" + "=" * 50)
    print("[SUCCESS] Scraping completed successfully!")
    print(f"Movies collected: {len(df)}")
    print(f"File saved to: {output_file}")
    print("=" * 50)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IMDb Top 250 Movie Scraper")
    parser.add_argument("--output", default="movies.csv", help="Path to output CSV file (default: movies.csv)")
    parser.add_argument("--visible", action="store_true", help="Run Chrome visibly instead of headless")
    parser.add_argument("--limit", type=int, default=250, help="Number of movies to scrape (default: 250)")
    args = parser.parse_args()

    success = scrape_imdb_top_250(
        output_file=args.output,
        headless=not args.visible,
        max_movies=args.limit
    )
    if not success:
        sys.exit(1)