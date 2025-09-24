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
