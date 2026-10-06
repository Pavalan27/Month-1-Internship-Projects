import os
import sys
import time
import pandas as pd
import streamlit as st

# --------------------------------
# Page Configuration
# --------------------------------
st.set_page_config(
    page_title="IMDb Top 250 Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e222d 0%, #262c3a 100%);
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #333d52;
    }
    .stDataFrame {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------
# Load CSV with Fallback Scraper
# --------------------------------
CSV_FILE = "movies.csv"

if not os.path.exists(CSV_FILE):
    st.title("🎬 IMDb Top 250 Movie Dashboard")
    st.warning("⚠️ `movies.csv` not found in workspace.")
    st.info("You can scrape IMDb Top 250 movies right now with one click, or run `python scraper.py` in your terminal.")
    
    col_scrape, _ = st.columns([2, 4])
    with col_scrape:
        if st.button("🚀 Scrape IMDb Top 250 Movies Now", type="primary", width="stretch"):
            with st.spinner("Scraping IMDb Top 250 movies in background... Please wait ~25-35 seconds."):
                import subprocess
                res = subprocess.run([sys.executable, "scraper.py"], capture_output=True, text=True)
                if res.returncode == 0 and os.path.exists(CSV_FILE):
                    st.success("✅ Scraping completed! Loading dashboard...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Scraper failed:\n{res.stderr or res.stdout}")
    st.stop()


@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(CSV_FILE)
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    if "Rating_Count" in df.columns:
        df["Rating_Count"] = pd.to_numeric(df["Rating_Count"], errors="coerce")
    return df

df = load_data()

# Column config for clean table presentation
COLUMN_CONFIG = {
    "Rank": st.column_config.NumberColumn("Rank", format="#%d"),
    "Title": st.column_config.TextColumn("Title"),
    "Year": st.column_config.NumberColumn("Year", format="%d"),
    "Rating": st.column_config.NumberColumn("Rating", format="⭐ %.1f"),
    "Duration": st.column_config.TextColumn("Duration"),
    "Certificate": st.column_config.TextColumn("Certificate"),
    "Genre": st.column_config.TextColumn("Genre"),
    "Rating_Count": st.column_config.NumberColumn("Votes", format="%d")
}

# --------------------------------
# Sidebar
# --------------------------------
st.sidebar.title("🎬 IMDb Top 250")
st.sidebar.caption("Interactive Movie Ratings Explorer")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Overview",
        "⭐ Rating Analysis",
        "🎭 Genre Analysis",
        "🎥 Movie Search",
        "📅 Year Analysis"
    ]
)

st.sidebar.divider()

# Quick stats in sidebar
st.sidebar.subheader("📌 Quick Info")
st.sidebar.write(f"**Total Movies:** {len(df)}")
if not df["Rating"].isna().all():
    st.sidebar.write(f"**Rating Range:** {df['Rating'].min():.1f} – {df['Rating'].max():.1f}")
if not df["Year"].isna().all():
    st.sidebar.write(f"**Year Range:** {int(df['Year'].min())} – {int(df['Year'].max())}")

st.sidebar.download_button(
    label="📥 Download Dataset (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="imdb_top_250.csv",
    mime="text/csv",
    width="stretch"
)

if st.sidebar.button("🔄 Refresh Data", width="stretch"):
    st.cache_data.clear()
    st.rerun()


# =================================
# 1. OVERVIEW
# =================================
if page == "🏠 Overview":
    st.title("🎬 IMDb Top 250 Movie Overview")
    st.write("Comprehensive analysis and ranking of the top-rated 250 movies on IMDb.")

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎬 Total Movies", len(df))
    with col2:
        avg_rating = df["Rating"].mean()
        st.metric("⭐ Average Rating", f"{avg_rating:.2f}")
    with col3:
        max_rating = df["Rating"].max()
        top_movie = df.loc[df["Rating"].idxmax()]["Title"] if not df["Rating"].isna().all() else "N/A"
        st.metric("🏆 Highest Rating", f"{max_rating:.1f}", help=f"Top rated: {top_movie}")
    with col4:
        min_rating = df["Rating"].min()
        st.metric("📉 Lowest in Top 250", f"{min_rating:.1f}")

    st.divider()

    # Filters
    st.subheader("🔍 Filter Movies")
    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
    
    with f_col1:
        min_rate = st.slider("Minimum Rating", min_value=8.0, max_value=9.5, value=8.0, step=0.1)
    
    with f_col2:
        min_y = int(df["Year"].min()) if not df["Year"].isna().all() else 1920
        max_y = int(df["Year"].max()) if not df["Year"].isna().all() else 2026
        selected_years = st.slider("Release Year Range", min_value=min_y, max_value=max_y, value=(min_y, max_y))

    with f_col3:
        # Extract unique genres
        all_genres = set()
        for g_str in df["Genre"].dropna():
            for g in str(g_str).split(","):
                g_clean = g.strip()
                if g_clean and g_clean != "N/A":
                    all_genres.add(g_clean)
        genre_filter = st.selectbox("Genre Filter", ["All"] + sorted(list(all_genres)))

    filtered_df = df[
        (df["Rating"] >= min_rate) &
        (df["Year"] >= selected_years[0]) &
        (df["Year"] <= selected_years[1])
    ]
    if genre_filter != "All":
        filtered_df = filtered_df[filtered_df["Genre"].astype(str).str.contains(genre_filter, case=False, na=False)]

    st.write(f"Showing **{len(filtered_df)}** of {len(df)} movies")

    # Display Table
    st.dataframe(
        filtered_df,
        width="stretch",
        hide_index=True,
        column_config=COLUMN_CONFIG
    )


# =================================
# 2. RATING ANALYSIS
# =================================
elif page == "⭐ Rating Analysis":
    st.title("⭐ Rating Analysis")
    st.write("Exploration of rating distribution, highest-scoring movies, and vote counts.")

    rating_df = df.sort_values("Rating", ascending=False)

    col_top, col_dist = st.columns([3, 2])

    with col_top:
        st.subheader("🏆 Top 20 Highest Rated Movies")
        cols_to_show = [c for c in ["Rank", "Title", "Year", "Rating", "Genre"] if c in rating_df.columns]
        st.dataframe(
            rating_df[cols_to_show].head(20),
            width="stretch",
            hide_index=True,
            column_config=COLUMN_CONFIG
        )

    with col_dist:
        st.subheader("📊 Rating Distribution")
        rating_counts = df["Rating"].value_counts().sort_index()
        st.bar_chart(rating_counts)

    if "Rating_Count" in df.columns and not df["Rating_Count"].isna().all():
        st.divider()
        st.subheader("🗳️ Most Voted Movies (Popularity)")
        voted_df = df.sort_values("Rating_Count", ascending=False).head(10)
        st.dataframe(
            voted_df[["Rank", "Title", "Year", "Rating", "Rating_Count"]],
            width="stretch",
            hide_index=True,
            column_config=COLUMN_CONFIG
        )


# =================================
# 3. GENRE ANALYSIS
# =================================
elif page == "🎭 Genre Analysis":
    st.title("🎭 Genre Analysis")
    st.write("Breakdown of IMDb Top 250 movies by genre and category performance.")

    # Flatten genres
    genre_rows = []
    for _, row in df.iterrows():
        genres_str = str(row.get("Genre", ""))
        if genres_str and genres_str != "N/A":
            for g in genres_str.split(","):
                g = g.strip()
                if g:
                    genre_rows.append({"Genre": g, "Rating": row["Rating"], "Title": row["Title"]})

    if genre_rows:
        gdf = pd.DataFrame(genre_rows)
        genre_count = gdf["Genre"].value_counts()
        genre_avg_rating = gdf.groupby("Genre")["Rating"].mean().sort_values(ascending=False)

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("📊 Most Common Genres")
            st.bar_chart(genre_count.head(15))

        with col_g2:
            st.subheader("⭐ Average Rating by Genre")
            st.bar_chart(genre_avg_rating.head(15))

        st.subheader("🎬 Explore Movies by Genre")
        picked_genre = st.selectbox("Select a Genre", sorted(gdf["Genre"].unique()))
        genre_matches = df[df["Genre"].astype(str).str.contains(picked_genre, case=False, na=False)]
        st.dataframe(
            genre_matches,
            width="stretch",
            hide_index=True,
            column_config=COLUMN_CONFIG
        )
    else:
        st.info("Genre data is currently not populated in the dataset.")


# =================================
# 4. MOVIE SEARCH
# =================================
elif page == "🎥 Movie Search":
    st.title("🎥 Search Movies")
    st.write("Search for your favorite movie by title, actor, or keyword.")

    search_query = st.text_input("🔍 Enter movie title or keyword", placeholder="e.g. Godfather, Dark Knight, Interstellar")

    if search_query.strip():
        results = df[
            df["Title"].str.contains(search_query.strip(), case=False, na=False) |
            df["Genre"].astype(str).str.contains(search_query.strip(), case=False, na=False)
        ]

        st.write(f"Found **{len(results)}** match{'es' if len(results) != 1 else ''}:")

        if not results.empty:
            for _, r in results.iterrows():
                with st.expander(f"#{int(r['Rank'])} - {r['Title']} ({int(r['Year']) if pd.notna(r['Year']) else 'N/A'}) - ⭐ {r['Rating']}", expanded=True):
                    st.write(f"**Genre:** {r.get('Genre', 'N/A')}")
                    st.write(f"**Duration:** {r.get('Duration', 'N/A')}  |  **Certificate:** {r.get('Certificate', 'N/A')}")
                    if pd.notna(r.get("Rating_Count")):
                        st.write(f"**Total Votes:** {int(r['Rating_Count']):,}")
        else:
            st.info("No movies found matching your search term. Try another title.")
    else:
        st.caption("Type a title above to begin searching.")


# =================================
# 5. YEAR ANALYSIS
# =================================
elif page == "📅 Year Analysis":
    st.title("📅 Release Year Analysis")
    st.write("Historical trends and releases across the decades in IMDb's Top 250.")

    valid_years = df["Year"].dropna().astype(int)
    year_counts = valid_years.value_counts().sort_index()

    col_y1, col_y2 = st.columns([3, 1])

    with col_y1:
        st.subheader("📈 Movies Count by Year")
        st.line_chart(year_counts)

    with col_y2:
        st.subheader("⏳ Milestones")
        oldest_idx = df["Year"].idxmin()
        newest_idx = df["Year"].idxmax()
        oldest_m = df.loc[oldest_idx]
        newest_m = df.loc[newest_idx]

        st.write("**Oldest Movie:**")
        st.write(f"🎬 {oldest_m['Title']} ({int(oldest_m['Year'])})")
        st.write(f"⭐ Rating: {oldest_m['Rating']}")
        st.divider()
        st.write("**Most Recent Movie:**")
        st.write(f"🎬 {newest_m['Title']} ({int(newest_m['Year'])})")
        st.write(f"⭐ Rating: {newest_m['Rating']}")

    st.divider()

    st.subheader("🔎 Browse Movies by Specific Year")
    unique_years = sorted(valid_years.unique(), reverse=True)
    chosen_year = st.selectbox("Select Year", unique_years)

    year_filtered = df[df["Year"] == chosen_year]
    st.write(f"**{len(year_filtered)}** movie{'s' if len(year_filtered) != 1 else ''} released in **{chosen_year}**:")

    st.dataframe(
        year_filtered,
        width="stretch",
        hide_index=True,
        column_config=COLUMN_CONFIG
    )