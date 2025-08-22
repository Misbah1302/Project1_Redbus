# 🚌 Redbus – Bus Booking System

A web-based **Bus Booking Application** built using **Python, Streamlit, MySQL, and Pandas**.  
This project mimics the functionality of real-world platforms like **Redbus**, allowing users to search for buses, apply filters, and book tickets through external links.

---

## 📌 Features

- 🔎 **Search & Filter Buses**
  - From City → To City
  - Bus Name
  - Bus Type (A/C Sleeper, Non A/C Sleeper, A/C Seater, Non A/C Seater, including all varieties)
  - Price Range (slider)
  - Rating Range (slider)
  - Seats Availability (number input)
  - Departure Time (Morning, Afternoon, Evening, Night)

- 🗄 **Database + CSV Fallback**
  - Fetches data from **MySQL database**
  - Falls back to `bus_data.csv` if DB connection is unavailable

- 🎨 **UI Enhancements**
  - Custom CSS styled **bus cards** with hover effects
  - Background image at **20% opacity** covering the entire screen
  - Clean sidebar layout for filters

- 📄 **Results Display**
  - Buses shown in attractive card format with:
    - Route
    - Departure, Duration, Arrival
    - Price
    - Seats Available
    - Star Rating
    - Direct **“Book Now”** link

---

## 📌 Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python (Pandas, PyMySQL)
- **Database:** MySQL (`bus_data` table)
- **Styling:** Custom HTML & CSS (injected via Streamlit)
- **Dataset:** `bus_data.csv` (fallback)

---

## 📌 Database Schema

**Table: `bus_data`**

| Column Name       | Data Type     | Description                         |
|-------------------|--------------|-------------------------------------|
| state             | VARCHAR(50)  | State of operation                  |
| route_name        | VARCHAR(100) | Route in format `From to To`        |
| route_link        | VARCHAR(255) | Booking link                        |
| busname           | VARCHAR(100) | Name of the bus operator            |
| bustype           | VARCHAR(50)  | Bus type (A/C Sleeper etc.)         |
| departing_time    | VARCHAR(10)  | Departure time (HH:MM)              |
| duration          | VARCHAR(20)  | Duration of journey                 |
| reaching_time     | VARCHAR(10)  | Arrival time                        |
| star_rating       | FLOAT        | Rating (0.0 – 5.0)                  |
| price             | INT          | Ticket price                        |
| seats_available   | INT          | Available seats                     |

---

