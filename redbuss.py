import streamlit as st
import pandas as pd
import pymysql
import os
import base64

# --- Encode bus.png to base64 ---
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

bus_base64 = get_base64_of_image("bus.png")

# --- Set Background Image with 20% opacity ---
st.markdown(f"""
    <style>
        /* Remove Streamlit default background */
        .stApp {{
            background: transparent !important;
        }}
        /* Background image */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url("data:image/png;base64,{bus_base64}") no-repeat center center fixed;
            background-size: cover;
            opacity: 0.2;   /* 👈 20% opacity */
            z-index: -1;    /* 👈 Always behind content */
        }}
    </style>
""", unsafe_allow_html=True)


# ==============================
# Main redbuss app
# ==============================

# --- Database Connection ---
def get_connection():
    try:
        return pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="bishh1310",  # your DB password
            database="transport_db",
            cursorclass=pymysql.cursors.DictCursor
        )
    except:
        return None 

# --- Fetch data from MySQL ---
def fetch_from_db():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT state, route_name, route_link, busname, bustype, 
               departing_time, duration, reaching_time, star_rating, price, seats_available
        FROM bus_data
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(rows)

# --- Load CSV fallback ---
def fetch_from_csv():
    if os.path.exists("bus_data.csv"):
        df = pd.read_csv("bus_data.csv")
        return df
    return pd.DataFrame()

# --- Filter Data ---
def filter_data(df, filters):
    if df.empty:
        return df

    if filters['from_city']:
        df = df[df['from_city'] == filters['from_city']]
    if filters['to_city']:
        df = df[df['to_city'] == filters['to_city']]
    if filters['busname']:
        df = df[df['busname'] == filters['busname']]
    if filters['bustype'] and filters['bustype'] != "Any":
        # Allow varieties of types (case-insensitive substring match)
        df = df[df['bustype'].str.contains(filters['bustype'], case=False, na=False)]
    if filters['min_price'] is not None:
        df = df[df['price'] >= filters['min_price']]
    if filters['max_price'] is not None:
        df = df[df['price'] <= filters['max_price']]
    if filters['min_rating'] is not None and filters['max_rating'] is not None:
        df = df[(df['star_rating'] >= filters['min_rating']) & (df['star_rating'] <= filters['max_rating'])]
    if filters['seats'] is not None:
        df = df[df['seats_available'] >= filters['seats']]

    if 'departing_time' in df.columns and filters['time_range'] and filters['time_range'] != "Any":
        def in_time_range(t):
            if pd.isna(t):
                return False
            try:
                hour = int(str(t).split(':')[0])
                if filters['time_range'] == "Morning (06:00-12:00)":
                    return 6 <= hour < 12
                elif filters['time_range'] == "Afternoon (12:00-18:00)":
                    return 12 <= hour < 18
                elif filters['time_range'] == "Evening (18:00-24:00)":
                    return 18 <= hour < 24
                elif filters['time_range'] == "Night (00:00-06:00)":
                    return 0 <= hour < 6
            except:
                return False
            return False
        df = df[df['departing_time'].apply(in_time_range)]
    return df

# --- Custom CSS for bus cards ---
st.markdown("""
    <style>
        .bus-card {
            background: #ffffffdd; /* slightly transparent white for readability */
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 12px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.2s ease-in-out;
        }
        .bus-card:hover {
            transform: scale(1.01);
            box-shadow: 0px 6px 16px rgba(0,0,0,0.15);
        }
        .bus-header {
            font-size: 20px;
            font-weight: bold;
            color: #d32f2f;
        }
        .route {
            font-size: 16px;
            color: #333;
        }
        .price {
            color: #2e7d32;
            font-size: 18px;
            font-weight: bold;
        }
        .rating {
            color: #fbc02d;
            font-size: 16px;
        }
        .book-btn {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 18px;
            background: #d32f2f;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
        }
        .book-btn:hover {
            background: #b71c1c;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Filters ---
st.sidebar.header("🧭 Filter Buses")

# Load data (DB first, then CSV fallback)
df_main = fetch_from_db()
if df_main.empty:
    st.warning("No data found in MySQL, using CSV fallback.")
    df_main = fetch_from_csv()

if df_main.empty:
    st.error("No bus data available.")
    st.stop()

# --- Extract from_city and to_city from route_name ---
if 'route_name' in df_main.columns:
    split_routes = df_main['route_name'].str.split(' to ', n=1, expand=True)
    df_main['from_city'] = split_routes[0].str.strip()
    df_main['to_city'] = split_routes[1].str.strip() if split_routes.shape[1] > 1 else None

# --- Clean up ---
for col in ["from_city", "to_city", "busname", "bustype"]:
    df_main[col] = (
        df_main[col]
        .astype(str)
        .str.strip()
        .replace(["nan", "None", "NaN", "NULL", "none"], "", regex=True)
    )

df_main = df_main[(df_main['from_city'] != "") & (df_main['to_city'] != "")]

# --- Build from_city → to_city map ---
city_map = {}
for _, row in df_main.iterrows():
    from_c = row['from_city']
    to_c = row['to_city']
    if from_c and to_c:
        city_map.setdefault(from_c, set()).add(to_c)

# --- From City filter ---
all_from_cities = sorted(df_main['from_city'].unique())
from_city = st.sidebar.selectbox("From City", [""] + list(all_from_cities))

# --- To City filter ---
to_cities = sorted(list(city_map.get(from_city, []))) if from_city else []
to_city = st.sidebar.selectbox("To City", [""] + to_cities)

# --- Bus Name filter ---
if from_city and to_city:
    filtered_busnames = sorted(df_main[(df_main['from_city'] == from_city) &
                                       (df_main['to_city'] == to_city)]['busname'].dropna().unique())
else:
    filtered_busnames = sorted(df_main['busname'].dropna().unique())
busname = st.sidebar.selectbox("Bus Name", [""] + list(filtered_busnames))

# --- Fixed Bus Type filter ---
bus_types = ["Any", "A/C Sleeper", "Non A/C Sleeper", "A/C Seater", "Non A/C Seater"]
bustype = st.sidebar.selectbox("Bus Type", bus_types)

with st.sidebar.form("bus_filter_form"):
    # Price slider
    min_price_val = int(df_main['price'].min()) if not df_main.empty else 0
    max_price_val = int(df_main['price'].max()) if not df_main.empty else 10000
    min_price, max_price = st.slider(
        "Price Range (₹)",
        min_value=min_price_val,
        max_value=max_price_val,
        value=(min_price_val, max_price_val),
        step=50
    )

    # Rating slider
    min_rating, max_rating = st.slider(
        "Rating Range (⭐)", 
        min_value=0.0, 
        max_value=5.0, 
        value=(0.0, 5.0), 
        step=0.5
    )

    # Seats limited to availability
    max_seats_available = int(df_main['seats_available'].max()) if not df_main.empty else 50
    seats = st.number_input("No. of seats", min_value=1, max_value=max_seats_available, value=1)

    time_range = st.selectbox("Departure Time", ["Any", "Morning (06:00-12:00)",
                                                 "Afternoon (12:00-18:00)",
                                                 "Evening (18:00-24:00)",
                                                 "Night (00:00-06:00)"])
    submit_button = st.form_submit_button(label="🔍 Search Buses")

# --- Main Content ---
st.title("🚌 Redbus – Book Your Ride")

if submit_button:
    filters = {
        "state": None,
        "from_city": from_city,
        "to_city": to_city,
        "busname": busname,
        "bustype": bustype if bustype != "Any" else None,
        "min_price": min_price,
        "max_price": max_price,
        "min_rating": min_rating,
        "max_rating": max_rating,
        "seats": seats,
        "time_range": time_range,
    }
    df = filter_data(df_main, filters)

    if not df.empty:
        for _, row in df.iterrows():
            stars = "⭐" * int(round(float(row["star_rating"]))) if pd.notna(row["star_rating"]) else "No rating"
            st.markdown(f"""
                <div class="bus-card">
                    <div class="bus-header">{row['busname']} ({row['bustype']})</div>
                    <p class="route">🛣️ {row['route_name']}</p>
                    <p>🕓 Departure: {row['departing_time']} | ⏳ Duration: {row['duration']} | 🎯 Arrival: {row['reaching_time']}</p>
                    <p class="price">💰 Price: ₹{row['price']}</p>
                    <p>🎟️ Seats Available: {row['seats_available']}</p>
                    <p class="rating">{stars}</p>
                    <a class="book-btn" href="{row['route_link']}" target="_blank">🚀 Book Now</a>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No buses match your filters.")
else:
    st.info("Use the filters on the left and click 'Search Buses' to view results.")
