import streamlit as st
import pandas as pd
import pandas.io.sql as sqlio
import altair as alt
import folium
from streamlit_folium import st_folium
from sqlalchemy import create_engine

# Assuming db.py contains your database connection setup
from db import conn_str

# Establishing a connection to your database
engine = create_engine(conn_str)

# Function to load data from the database
def load_data():
    query = "SELECT * FROM events"
    df = sqlio.read_sql_query(query, conn_str)
    df['date'] = pd.to_datetime(df['date'])
    
    # Ensure 'weathercondition' column exists, if not, initialize it with 'Not Available'
    if 'weathercondition' not in df.columns:
        df['weathercondition'] = 'Not Available'
    
    # Check if 'geolocation' column exists, if not, initialize it with None values
    if 'geolocation' not in df.columns:
        df['geolocation'] = None
    else:
        # If 'geolocation' column exists, ensure it's in string format
        df['geolocation'] = df['geolocation'].astype(str)
    
    return df

# Function to render charts
def render_event_categories_chart(df):
    chart = alt.Chart(df).mark_bar().encode(
        x="count()",
        y=alt.Y("category", sort='-x')
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

def render_event_months_chart(df):
    df['month_year'] = df['date'].dt.strftime('%Y-%m')
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('month_year:N', sort='-y', title='Month-Year'),
        y='count()'
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

def render_event_weekdays_chart(df):
    df['day_of_week'] = df['date'].dt.day_name()
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('day_of_week:N', sort=None, title='Day of the Week'),
        y='count()'
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

# Function to apply filters and return filtered DataFrame
def filter_data(df, category, date_range, location, weather_condition):
    filtered_df = df.copy()
    if category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == category]
    
    # Convert selected_date_range to date objects for comparison
    if date_range:
        start_date, end_date = date_range[0], date_range[1]
        filtered_df = filtered_df[(filtered_df['date'].dt.date >= start_date) & (filtered_df['date'].dt.date <= end_date)]

    if location != 'All':
        filtered_df = filtered_df[filtered_df['location'] == location]
    if weather_condition != 'All':
        filtered_df = filtered_df[filtered_df['weathercondition'] == weather_condition]
    return filtered_df

# Create and display the map
def display_map(df):
    map_center = [47.6062, -122.3321]  # Center of Seattle
    m = folium.Map(location=map_center, zoom_start=10)
    for idx, row in df.iterrows():
        if row['geolocation'] and row['geolocation'] != 'None':
            lat, lon = map(float, row['geolocation'].strip('()').split(','))
            folium.Marker(
                [lat, lon],
                popup=f"{row['title']} - {row['date'].strftime('%Y-%m-%d')}",
            ).add_to(m)
    st_folium(m, width=725, height=500)

def main():
    st.title("Seattle Events")

    df = load_data()

    # Filters
    categories = ['All'] + sorted(df['category'].unique())
    locations = ['All'] + sorted(df['location'].unique())
    weather_conditions = ['All'] + sorted(df.get('weathercondition', pd.Series(['Not Available'])).unique())

    selected_category = st.sidebar.selectbox("Select a category", categories, index=0, key='category_select')
    selected_location = st.sidebar.selectbox("Select a location", locations, index=0, key='location_select')
    selected_weather_condition = st.sidebar.selectbox("Select a weather condition", weather_conditions, index=0, key='weather_condition_select')
    min_date, max_date = df['date'].min().date(), df['date'].max().date()
    selected_date_range = st.sidebar.date_input("Select date range", [min_date, max_date])

    filtered_df = filter_data(df, selected_category, selected_date_range, selected_location, selected_weather_condition)

    # Render charts
    render_event_categories_chart(filtered_df)
    render_event_months_chart(filtered_df)
    render_event_weekdays_chart(filtered_df)

    st.dataframe(filtered_df)

    display_map(filtered_df)

if __name__ == "__main__":
    main()


