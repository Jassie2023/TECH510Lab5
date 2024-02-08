import requests
import json
import re
import datetime
from zoneinfo import ZoneInfo
import html
from db import get_db_conn

URL = 'https://visitseattle.org/events/page/'
URL_LIST_FILE = './data/links.json'
URL_DETAIL_FILE = './data/data.json'

def list_links():
    res = requests.get(URL + '1/')
    last_page_no = int(re.findall(r'bpn-last-page-link"><a href=".+?/page/(\d+?)/.+" title="Navigate to last page">', res.text)[0])

    links = []
    for page_no in range(1, last_page_no + 1):
        res = requests.get(URL + str(page_no) + '/')
        links.extend(re.findall(r'<h3 class="event-title"><a href="(https://visitseattle.org/events/.+?/)" title=".+?">.+?</a></h3>', res.text))

    with open(URL_LIST_FILE, 'w') as file:
        json.dump(links, file)

def get_lat_lon(location_name):
    base_url = "https://nominatim.openstreetmap.org/search.php"
    query_params = {"q": f"{location_name}, Seattle", "format": "jsonv2"}
    res = requests.get(base_url, params=query_params)
    if res.json():
        lat = res.json()[0]["lat"]
        lon = res.json()[0]["lon"]
        return lat, lon
    return None, None

def get_weather_data(lat, lon):
    base_url = f"https://api.weather.gov/points/{lat},{lon}"
    res = requests.get(base_url)
    if res.status_code == 200:
        forecast_url = res.json()['properties']['forecast']
        forecast_res = requests.get(forecast_url)
        if forecast_res.status_code == 200:
            forecast_data = forecast_res.json()['properties']['periods'][0]
            return {
                'shortForecast': forecast_data['shortForecast'],
                'temperature': forecast_data['temperature'],
                'windSpeed': forecast_data['windSpeed'],
                'windDirection': forecast_data['windDirection']
            }
    return None

def get_detail_page():
    with open(URL_LIST_FILE, 'r') as file:
        links = json.load(file)

    data = []
    for link in links:
        try:
            res = requests.get(link)
            row = {}
            row['title'] = html.unescape(re.findall(r'<h1 class="page-title" itemprop="headline">(.+?)</h1>', res.text)[0])
            datetime_venue = re.findall(r'<h4><span>.*?(\d{1,2}/\d{1,2}/\d{4})</span> \| <span>(.+?)</span></h4>', res.text)[0]
            row['date'] = datetime.datetime.strptime(datetime_venue[0], '%m/%d/%Y').replace(tzinfo=ZoneInfo('America/Los_Angeles')).isoformat()
            row['venue'] = datetime_venue[1].strip()
            metas = re.findall(r'<a href=".+?" class="button big medium black category">(.+?)</a>', res.text)
            row['category'] = html.unescape(metas[0])
            row['location'] = metas[1]
            lat, lon = get_lat_lon(row['location'])
            if lat and lon:
                row['latitude'], row['longitude'] = lat, lon
                weather_data = get_weather_data(lat, lon)
                if weather_data:
                    row.update(weather_data)  # Add weather data to the event info
            data.append(row)
        except Exception as e:
            print(f"Error processing {link}: {e}")

    with open(URL_DETAIL_FILE, 'w') as file:
        json.dump(data, file)

def insert_to_pg():
    conn = get_db_conn()
    cur = conn.cursor()

    with open(URL_DETAIL_FILE, 'r') as file:
        data = json.load(file)

    for row in data:
        # Adjust your SQL INSERT statement as needed to match your table's schema
        cur.execute('''
        INSERT INTO events (title, date, venue, category, location, latitude, longitude, weather_condition, temperature, wind_speed, wind_direction)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (title) DO NOTHING;
        ''', (
            row['title'],
            row['date'],
            row['venue'],
            row['category'],
            row['location'],
            row.get('latitude'),
            row.get('longitude'),
            row.get('shortForecast'),
            row.get('temperature'),
            row.get('windSpeed'),
            row.get('windDirection'),
        ))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    list_links()
    get_detail_page()
    insert_to_pg()
