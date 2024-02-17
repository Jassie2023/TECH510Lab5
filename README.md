# TECHIN 510 Lab 5 Seattle Events Dashboard

Jassie He

This is a Streamlit-based web application that displays information about events happening in Seattle. It uses data scraped from online sources, stored in a PostgreSQL database, and presents various insights about event categories, dates, and weather conditions.

# How to Run

## Setup
Clone the repository and navigate to it.

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
.\venv\Scripts\activate  # On Windows
```

Install dependencies:

```bash
pip install -r requirements.txt

```

## Database Preparation
Make sure PostgreSQL is installed and running.

Adjust database settings in db.py or through environment variables.

Populate the database by running:

```bash
python scraper.py
```

## Running the Application
Start the Streamlit app:

```bash
streamlit run app.py
```
Access the web interface via http://localhost:8501.


# Components
app.py: Main application script.
scraper.py: For fetching and storing event data.
db.py: Handles database connectivity.


# Notes
Customize the appearance and functionality of the dashboard through Streamlit's widgets and layout options.
Secure database credentials using environment variables, not tracked in version control.
