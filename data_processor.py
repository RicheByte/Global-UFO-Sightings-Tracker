import pandas as pd
import sqlite3
import re

def clean_data(df):
    """
    Cleans the UFO sightings DataFrame.
    - Renames columns for consistency.
    - Handles missing latitude/longitude (drops rows).
    - Converts 'datetime' to datetime objects and normalizes date format.
    - Fills missing 'shape' with 'unknown'.
    - Removes duplicates.
    - Cleans 'comments' column.
    """
    print("Starting data cleaning...")

    # Rename columns for easier access
    # **FIX:** Added .str.strip() to remove leading/trailing whitespace from headers
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    df = df.rename(columns={'duration_seconds': 'duration_s', 'duration_hours/min': 'duration_h_m', 'comments': 'description', 'date_posted': 'date_posted_str'})

    # Convert 'datetime' to proper datetime objects
    # Handle potential errors during conversion by setting errors='coerce'
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df['date'] = df['datetime'].dt.normalize() # Extract date only
    df = df.dropna(subset=['datetime']) # Drop rows where datetime conversion failed

    # Ensure latitude and longitude are numeric and drop NaNs
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Filter out invalid lat/lon values (e.g., latitude outside -90 to 90)
    df = df[(df['latitude'] >= -90) & (df['latitude'] <= 90)]
    df = df[(df['longitude'] >= -180) & (df['longitude'] <= 180)]

    # Fill missing shapes with 'unknown'
    df['shape'] = df['shape'].fillna('unknown').str.lower().str.strip()

    # Clean description (comments)
    df['description'] = df['description'].fillna('').apply(lambda x: re.sub(r'[^\w\s.,!?]', '', str(x).strip()))
    df['description'] = df['description'].str.replace('&#44', ',').str.replace('&quot;', '"').str.replace('&#33;', '!') # HTML entities

    # Convert duration_s to numeric, filling NaNs with 0
    df['duration_s'] = pd.to_numeric(df['duration_s'], errors='coerce').fillna(0)

    # Convert date_posted to datetime if it exists, otherwise drop or ignore
    if 'date_posted_str' in df.columns:
        df['date_posted'] = pd.to_datetime(df['date_posted_str'], errors='coerce')
    else:
        df['date_posted'] = pd.NaT # Set to Not a Time if column doesn't exist

    # Drop duplicates based on a subset of columns
    df = df.drop_duplicates(subset=['datetime', 'latitude', 'longitude', 'description'])

    # Select relevant columns for the database
    cleaned_df = df[['datetime', 'date', 'city', 'state', 'country', 'shape', 
                     'duration_s', 'description', 'latitude', 'longitude', 'date_posted']]
    
    print(f"Data cleaning complete. Original rows: {len(raw_df)} -> Cleaned rows: {len(cleaned_df)}")
    return cleaned_df

def create_sqlite_db(df, db_name='ufo_sightings.db'):
    """
    Creates an SQLite database from the cleaned DataFrame.
    """
    print(f"Creating SQLite database: {db_name}...")
    conn = sqlite3.connect(db_name)
    df.to_sql('sightings', conn, if_exists='replace', index=False)
    conn.close()
    print("SQLite database created successfully.")

if __name__ == '__main__':
    csv_path = 'data/ufo_sightings.csv'
    db_path = 'ufo_sightings.db'
    cleaned_csv_path = 'data/ufo_cleaned.csv'

    try:
        # Load data
        raw_df = pd.read_csv(csv_path, low_memory=False)
        print(f"Loaded {len(raw_df)} raw sightings from {csv_path}")

        # Clean data
        cleaned_df = clean_data(raw_df.copy()) # Use .copy() to avoid SettingWithCopyWarning

        # Save cleaned data to CSV
        cleaned_df.to_csv(cleaned_csv_path, index=False)
        print(f"Cleaned data saved to {cleaned_csv_path}")

        # Create SQLite DB
        create_sqlite_db(cleaned_df, db_path)
        print("Preprocessing complete!")

    except FileNotFoundError:
        print(f"Error: '{csv_path}' not found. Please ensure the dataset is in the 'data/' folder.")
    except Exception as e:
        print(f"An error occurred during preprocessing: {e}")