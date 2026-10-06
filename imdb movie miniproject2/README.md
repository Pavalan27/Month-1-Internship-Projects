# 🎬 IMDb Top 250 Movie Scraper & Interactive Dashboard

An end-to-end Python web scraping and data analytics application that extracts the official **IMDb Top 250 Movies** and provides a rich, interactive **Streamlit Dashboard** for visualization and exploration.

---

## 📌 Project Overview

This project consists of two core components:
1. **`scraper.py`**: A robust Selenium-powered scraper that navigates IMDb's Top 250 chart, evades anti-bot detection, extracts structured metadata (Rank, Title, Year, Rating, Duration, Certificate, Genre, Rating Count), and exports the dataset to `movies.csv`.
2. **`dashboard.py`**: A feature-rich Streamlit web dashboard for exploring, filtering, analyzing, and searching the scraped movie data with interactive charts and visualizations.

---

## 🚀 Features

- **Anti-Detection Web Scraping**: Configured with stealth Chrome options, automation flag suppression, realistic user-agents, and lazy-loading scrolling to reliably extract all 250 movies.
- **Dual-Layer Extraction**: Uses high-fidelity JSON-LD structured data coupled with modern DOM selectors for 100% data completeness.
- **Automated Fallback**: If `movies.csv` does not exist when starting the dashboard, a one-click button allows you to scrape data directly from the web UI.
- **Interactive Multi-Page Dashboard**:
  - 🏠 **Overview**: Summary metrics, interactive filters (rating, year range, genre), and formatted data table.
  - ⭐ **Rating Analysis**: Top 20 highest-rated movies, rating distribution histogram, and popularity rankings by vote counts.
  - 🎭 **Genre Analysis**: Most common genres and average ratings across categories.
  - 🎥 **Movie Search**: Fast title, keyword, and genre lookup with expandable detail cards.
  - 📅 **Year Analysis**: Release trend timeline, milestones (oldest vs newest), and year-specific filtering.
  - 📥 **One-Click CSV Export**: Download the full dataset anytime from the sidebar.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.9 or higher
- Google Chrome browser installed on your machine

### 2. Install Dependencies
Clone or navigate to the project directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## 📖 Usage Instructions

### Step 1: Run the Scraper (Generate Data)
Run `scraper.py` in your terminal to collect the latest IMDb Top 250 movies:

```bash
python scraper.py
```

#### Optional Command-Line Arguments:
- `--limit N`: Scrape only the first *N* movies (e.g., `python scraper.py --limit 50`).
- `--visible`: Open Chrome in a visible window rather than headless mode (useful for debugging).
- `--output filename.csv`: Specify a custom output CSV path (default: `movies.csv`).

Example:
```bash
python scraper.py --limit 250
```

### Step 2: Launch the Interactive Dashboard
Launch the Streamlit web dashboard:

```bash
streamlit run dashboard.py
```

Once executed, Streamlit will open automatically in your default browser at `http://localhost:8501`.

---

## 📁 File Structure

```text
├── scraper.py          # Selenium scraper with anti-detection & JSON-LD parsing
├── dashboard.py        # Streamlit web application with interactive charts
├── movies.csv          # Generated dataset containing IMDb Top 250 movies
├── requirements.txt    # Required Python packages
└── README.md           # Project documentation and guide
```

---

## 📊 Dataset Schema (`movies.csv`)

| Column | Type | Description |
|---|---|---|
| `Rank` | Integer | Position on IMDb Top 250 chart (#1 to #250) |
| `Title` | String | Official movie title |
| `Year` | Integer | Release year (e.g. 1994) |
| `Rating` | Float | IMDb average rating (e.g. 9.3) |
| `Duration` | String | Runtime (e.g. "2h 22m") |
| `Certificate` | String | Age rating / classification (e.g. "R", "PG-13") |
| `Genre` | String | Comma-separated list of genres |
| `Rating_Count` | Integer | Number of user votes cast |
