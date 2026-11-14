
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Konfigurasi halaman
st.set_page_config(
    page_title="Bike Sharing Analytics",
    page_icon="🚲",
    layout="wide"
)

# Membaca dataset
BASE_DIR = Path(__file__).resolve().parent.parent
day_path = BASE_DIR / "data" / "day.csv"
hour_path = BASE_DIR / "data" / "hour.csv"

day_df = pd.read_csv(day_path)
hour_df = pd.read_csv(hour_path)

# Mengubah tanggal
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

# Label musim
season_map = {
    1: "Spring",
    2: "Summer",
    3: "Fall",
    4: "Winter"
}

weather_map = {
    1: "Clear",
    2: "Mist/Cloudy",
    3: "Light Snow/Rain",
    4: "Heavy Rain"
}

day_df["season_label"] = day_df["season"].map(season_map)
hour_df["season_label"] = hour_df["season"].map(season_map)

day_df["weather_label"] = day_df["weathersit"].map(weather_map)
hour_df["weather_label"] = hour_df["weathersit"].map(weather_map)

# Judul dashboard
st.title("🚲 Bike Sharing Analytics Dashboard")
st.markdown(
    "Dashboard analisis pola penyewaan sepeda "
    "berdasarkan waktu, musim, dan kondisi cuaca."
)

# Filter
st.sidebar.header("Filter Data")

selected_year = st.sidebar.multiselect(
    "Pilih Tahun",
    options=sorted(hour_df["yr"].unique()),
    default=sorted(hour_df["yr"].unique()),
    format_func=lambda x: str(int(x) + 2011)
)

selected_season = st.sidebar.multiselect(
    "Pilih Musim",
    options=hour_df["season_label"].dropna().unique(),
    default=hour_df["season_label"].dropna().unique()
)

selected_weather = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca",
    options=hour_df["weather_label"].dropna().unique(),
    default=hour_df["weather_label"].dropna().unique()
)

# Filter data
filtered_hour = hour_df[
    (hour_df["yr"].isin(selected_year)) &
    (hour_df["season_label"].isin(selected_season)) &
    (hour_df["weather_label"].isin(selected_weather))
].copy()

filtered_day = day_df[
    (day_df["yr"].isin(selected_year)) &
    (day_df["season_label"].isin(selected_season)) &
    (day_df["weather_label"].isin(selected_weather))
].copy()

if filtered_hour.empty:
    st.warning("Tidak ada data untuk kombinasi filter tersebut.")
    st.stop()

# KPI
total_rentals = filtered_hour["cnt"].sum()
registered = filtered_hour["registered"].sum()
casual = filtered_hour["casual"].sum()
average_rentals = filtered_hour["cnt"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Rentals", f"{total_rentals:,.0f}")
col2.metric("Registered Users", f"{registered:,.0f}")
col3.metric("Casual Users", f"{casual:,.0f}")
col4.metric("Average Rentals", f"{average_rentals:,.1f}")

st.divider()

# Grafik 1: Pola penyewaan berdasarkan jam
st.subheader("1. Hourly Rental Patterns")

hourly_data = (
    filtered_hour.groupby(["hr", "workingday"])["cnt"]
    .mean()
    .reset_index()
)

hourly_data["Day Type"] = hourly_data["workingday"].map({
    0: "Non-Working Day",
    1: "Working Day"
})

fig1 = px.line(
    hourly_data,
    x="hr",
    y="cnt",
    color="Day Type",
    markers=True,
    labels={
        "hr": "Hour",
        "cnt": "Average Rentals",
        "Day Type": "Day Type"
    }
)

st.plotly_chart(fig1, width="stretch")

# Grafik 2: Penyewaan berdasarkan musim
st.subheader("2. Rentals by Season")

season_data = (
    filtered_day.groupby("season_label")["cnt"]
    .mean()
    .reset_index()
)

fig2 = px.bar(
    season_data,
    x="season_label",
    y="cnt",
    color_discrete_sequence=["#2878B5"],
    labels={
        "season_label": "Season",
        "cnt": "Average Daily Rentals"
    }
)

st.plotly_chart(fig2, width="stretch")

# Grafik 3: Penyewaan berdasarkan cuaca
st.subheader("3. Rentals by Weather")

weather_data = (
    filtered_day.groupby("weather_label")["cnt"]
    .mean()
    .reset_index()
)

fig3 = px.bar(
    weather_data,
    x="weather_label",
    y="cnt",
    color_discrete_sequence=["#2878B5"],
    labels={
        "weather_label": "Weather",
        "cnt": "Average Daily Rentals"
    }
)

st.plotly_chart(fig3, width="stretch")

# Grafik 4: Perbandingan penyewaan berdasarkan hari
st.subheader("4. Working Day vs Non-Working Day")

day_type_data = (
    filtered_hour.groupby("workingday")["cnt"]
    .mean()
    .reset_index()
)

day_type_data["Day Type"] = day_type_data["workingday"].map({
    0: "Non-Working Day",
    1: "Working Day"
})

fig4 = px.bar(
    day_type_data,
    x="Day Type",
    y="cnt",
    color_discrete_sequence=["#2878B5"],
    labels={
        "cnt": "Average Hourly Rentals",
        "Day Type": "Day Type"
    }
)

st.plotly_chart(fig4, width="stretch")

st.caption(
    "Source: Bike Sharing Dataset (2011–2012). "
    "Analysis is descriptive and does not establish causality."
)
