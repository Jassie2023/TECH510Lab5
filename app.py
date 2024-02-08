import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import altair as alt
import folium
from streamlit_folium import st_folium
import os

# Setting up database connection string
db_user = os.getenv('DB_USER', 'serverloginname') 
db_pw = os.getenv('DB_PASSWORD', 'A123456#')  
db_host = os.getenv('DB_HOST', 'techin510lab4.postgres.database.azure.com')  
db_port = os.getenv('DB_PORT', '5432') 
db_name = os.getenv('DB_NAME', 'postgres')
conn_str = f'postgresql://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}'

# Creating a database engine using SQLAlchemy
engine = create_engine(conn_str)

st.title("Seattle Events Dashboard")

# Function to load data from the database with caching
@st.cache_data
def load_data():
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM events", conn)

df = load_data().copy()

# create chart
# 1. event
st.subheader("Event Category Distribution")
category_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("count()", title="Number of Events"),
    y=alt.Y("category", sort='-x', title="Category")
).interactive()
st.altair_chart(category_chart, use_container_width=True)

# 2. monthly
df['month'] = pd.to_datetime(df['date']).dt.month_name()
month_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("month", sort='-y', title="Month"),
    y=alt.Y("count()", title="Number of Events"),
    color="month"
).interactive()
st.subheader("Events by Month")
st.altair_chart(month_chart, use_container_width=True)

# 3. weekly
df['weekday'] = pd.to_datetime(df['date']).dt.day_name()
weekday_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("weekday", sort='-y', title="Day of the Week"),
    y=alt.Y("count()", title="Number of Events"),
    color="weekday"
).interactive()
st.subheader("Events by Day of the Week")
st.altair_chart(weekday_chart, use_container_width=True)

# components
# selectbox
category = st.selectbox("Select a Category", ['All'] + list(df['category'].unique()))

# data range
date_range = st.date_input("Select Date Range", [])

# 过滤位置
location = st.selectbox("Select a Location", ['All'] + list(df['location'].unique()))

# filter
if category != 'All':
    df = df[df['category'] == category]

# Check if both start and end dates have been selected
if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0]).tz_localize('UTC')
    end_date = pd.to_datetime(date_range[1]).tz_localize('UTC')
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# show data
st.subheader("Filtered Events")
st.write(df)

# map
m = folium.Map(location=[47.6062, -122.3321], zoom_start=12)
folium.Marker([47.6062, -122.3321], popup='Seattle').add_to(m)
st_folium(m, width=700, height=500)

