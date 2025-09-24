
# Global UFO Sightings Tracker (Product V1)

An interactive web application built with Streamlit and Folium to visualize UFO sightings worldwide. Users can explore sightings by location, date range, shape, and search keywords, with real-time statistics.

## 🎯 Features (MVP Product V1)

-   **Interactive Map:** Displays UFO sightings using Folium, with marker clustering for high-density areas.
-   **Date Range Filter:** Explore sightings within specific years.
-   **Location Filters:** Filter by country and state.
-   **Sighting Shape Filter:** Narrow down sightings by the reported shape of the UFO.
-   **Keyword Search:** Search for specific terms in sighting descriptions.
-   **Dynamic Statistics:**
    -   Top 10 Countries by Sightings.
    -   UFO Sightings Timeline Trend.
    -   Top 10 Sighting Shapes.
-   **Cleaned Data & Database:** Processes raw CSV into a clean CSV and an efficient SQLite database.

## 🛠️ Technologies Used

-   **Python:** Core language for data processing and the web app.
-   **Pandas:** For data manipulation and cleaning.
-   **SQLite3:** Lightweight database for efficient data storage and retrieval.
-   **Folium & Streamlit-Folium:** For interactive map visualization with marker clustering.
-   **Streamlit:** For building the interactive web application and frontend.
-   **Plotly Express:** For generating interactive charts for statistics.

## 🚀 Setup and Run Locally

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository (or create the structure)

```bash
git clone <your-repo-link> # If you put it on GitHub
cd ufo-interactive-map
```
If you're creating it manually as guided above, ensure your directory structure matches:
```
ufo-interactive-map/
│── data/
│   └── ufo_sightings.csv
│── ufo_sightings.db          # Will be generated
│── data_processor.py
│── app.py
│── requirements.txt
│── README.md
```

### 2. Create a Virtual Environment and Install Dependencies

```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Data Collection

-   **Download the Dataset:** Obtain a UFO sightings dataset in CSV format. A commonly used one can be found on Kaggle (e.g., `nuforc_reports.csv` or similar).
-   **Place the CSV:** Save the downloaded CSV file as `ufo_sightings.csv` inside the `data/` folder.
    (e.g., `ufo-interactive-map/data/ufo_sightings.csv`)

### 4. Data Preprocessing

Run the data processing script to clean the raw data and create the SQLite database:

```bash
python data_processor.py
```
This script will:
-   Read `data/ufo_sightings.csv`.
-   Clean missing values, normalize formats, and remove duplicates.
-   Save the cleaned data to `data/ufo_cleaned.csv`.
-   Create `ufo_sightings.db` (a SQLite database) in the project root.

### 5. Run the Streamlit Application

```bash
streamlit run app.py
```
This command will open the interactive map application in your default web browser (usually at `http://localhost:8501`).


