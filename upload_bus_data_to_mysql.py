
import pandas as pd
from sqlalchemy import create_engine

# Load the CSV
df = pd.read_csv("bus_data.csv")

# Create SQLAlchemy engine (update credentials as needed)
engine = create_engine("mysql+mysqlconnector://root:bishh1310@127.0.0.1:3306/transport_db")


# Write DataFrame to MySQL
df.to_sql("bus_data", con=engine, if_exists="append", index=False)

print("Data uploaded successfully!")

