
import pandas as pd
import pymysql

data = pd.read_csv("bus_data.csv")

# Add from_city/to_city columns in DataFrame
split_routes = data['route_name'].str.split(' to ', n=1, expand=True)
data['from_city'] = split_routes[0].str.strip()
data['to_city'] = split_routes[1].str.strip() if split_routes.shape[1] > 1 else None

conn = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="bishh1310",
    database="transport_db"
)
cur = conn.cursor()

for _, row in data.iterrows():
    insert_query = """
    INSERT INTO bus_data(
        state, from_city, to_city, route_name, route_link, busname, bustype,
        departing_time, duration, reaching_time, star_rating, price, seats_available
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    values = (
        row['state'], row['from_city'], row['to_city'], row['route_name'], row['route_link'],
        row['busname'], row['bustype'], row['departing_time'], row['duration'], row['reaching_time'],
        row['star_rating'], row['price'], row['seats_available']
    )
    cur.execute(insert_query, values)

conn.commit()
cur.close()
conn.close()
print("Data inserted successfully.")
