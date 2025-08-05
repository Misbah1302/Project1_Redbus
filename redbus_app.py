import streamlit as st
import pandas as pd
import pymysql

# --- Database Connection ---
def get_connection():
    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="bishh1310",  # Your DB password
        database="transport_db",
        cursorclass=pymysql.cursors.DictCursor
    )

# --- Extract from_city and to_city from route_name ---
def get_city_options():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT route_name FROM bus_data")
    route_names = [row['route_name'] for row in cursor.fetchall()]

    from_cities = set()
    to_cities = set()

    for route in route_names:
        if " to " in route:
            from_c, to_c = route.split(" to ")
            from_cities.add(from_c.strip())
            to_cities.add(to_c.strip())

    cursor.close()
    conn.close()
    return sorted(from_cities), sorted(to_cities)

# --- Fetch Data with Filters ---
def get_filtered_data(filters):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT route_name, route_link, busname, bustype, departing_time, 
               duration, reaching_time, star_rating, price, seats_available
        FROM bus_data
        WHERE 1=1
    """
    params = []

    if filters['from_city']:
        query += " AND route_name LIKE %s"
        params.append(filters['from_city'] + " to %")
    if filters['to_city']:
        query += " AND route_name LIKE %s"
        params.append("% to " + filters['to_city'])
    if filters['busname']:
        query += " AND busname = %s"
        params.append(filters['busname'])
    if filters['bustype']:
        query += " AND bustype LIKE %s"
        params.append(f"%{filters['bustype']}%")
    if filters['min_price'] is not None:
        query += " AND price >= %s"
        params.append(filters['min_price'])
    if filters['max_price'] is not None:
        query += " AND price <= %s"
        params.append(filters['max_price'])
    if filters['rating'] is not None:
        query += " AND star_rating >= %s"
        params.append(filters['rating'])
    if filters['seats'] is not None:
        query += " AND seats_available >= %s"
        params.append(filters['seats'])

    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return pd.DataFrame(data)

# --- Sidebar Filters ---
st.sidebar.header("🧭 Filter Buses")
from_cities, to_cities = get_city_options()

with st.sidebar.form("bus_filter_form"):
    from_city = st.selectbox("From City", [""] + from_cities)
    to_city = st.selectbox("To City", [""] + to_cities)
    busname = st.text_input("Bus Name")
    bustype = st.selectbox("Bus Type", ["", "A/C", "Non A/C", "Sleeper", "Seater"])
    min_price = st.number_input("Min Price", min_value=0, value=0)
    max_price = st.number_input("Max Price", min_value=0, value=10000)
    rating = st.number_input("Rating", min_value=0.0, max_value=5.0, value=0.1)
    seats = st.number_input("No. of seats", min_value=0, max_value=100, value=1)
    
    submit_button = st.form_submit_button(label="🔍 Search Buses")

# --- Main Content ---
st.title("🚌 Redbus")

if submit_button:
    filters = {
        "from_city": from_city,
        "to_city": to_city,
        "busname": busname,
        "bustype": bustype,
        "min_price": min_price,
        "max_price": max_price,
        "rating": rating,
        "seats": seats
    }

    df = get_filtered_data(filters)

    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No buses match your filters.")
else:
    st.info("Use the filters on the left and click 'Search Buses' to view results.")
