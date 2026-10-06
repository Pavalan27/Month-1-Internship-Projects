import streamlit as st
import pandas as pd

# Page settings
st.set_page_config(
    page_title="Cryptocurrency Price Tracker",
    page_icon="₿",
    layout="wide"
)

# Load CSV
df = pd.read_csv("crypto_data.csv")

# Title
st.title("₿ Cryptocurrency Price Tracker")
st.write("Top 10 cryptocurrency market monitoring dashboard")

# Sidebar
st.sidebar.title("📊 Crypto Dashboard")

page = st.sidebar.radio(
    "Select Dashboard",
    [
        "🏠 Overview",
        "💰 Price Analysis",
        "📈 24h Change",
        "💵 Market Cap"
    ]
)

# =========================
# OVERVIEW
# =========================

if page == "🏠 Overview":

    st.header("🏠 Market Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🪙 Total Coins", len(df))

    with col2:
        st.metric("🌐 Data Source", "CoinGecko")

    with col3:
        st.metric("📊 Data Type", "Scraped Data")

    st.subheader("Top 10 Cryptocurrencies")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# =========================
# PRICE ANALYSIS
# =========================

elif page == "💰 Price Analysis":

    st.header("💰 Price Analysis")

    df["Price_Number"] = (
        df["Price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    chart = df[["Coin", "Price_Number"]].set_index("Coin")

    st.bar_chart(chart)

    st.subheader("Cryptocurrency Prices")

    st.dataframe(
        df[["Rank", "Coin", "Price"]],
        use_container_width=True,
        hide_index=True
    )


# =========================
# 24 HOUR CHANGE
# =========================

elif page == "📈 24h Change":

    st.header("📈 24-Hour Price Change")

    df["Change_Number"] = (
        df["24h Change"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .astype(float)
    )

    chart = df[
        ["Coin", "Change_Number"]
    ].set_index("Coin")

    st.bar_chart(chart)

    st.subheader("24-Hour Change")

    st.dataframe(
        df[["Rank", "Coin", "24h Change"]],
        use_container_width=True,
        hide_index=True
    )


# =========================
# MARKET CAP
# =========================

elif page == "💵 Market Cap":

    st.header("💵 Market Capitalization")

    st.subheader("Market Cap of Top 10 Cryptocurrencies")

    st.dataframe(
        df[["Rank", "Coin", "Market Cap"]],
        use_container_width=True,
        hide_index=True
    )