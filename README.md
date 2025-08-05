# RedBus – Bus Search and Filter Application
# Objective
To develop a web-based application that allows users to search and filter bus services based on
multiple criteria such as city, price, type, rating, and seat availability using an intuitive interface.
# Tools & Technologies Used
- Frontend/UI: Streamlit (Python framework for interactive web apps)
- Backend: Python
- Database: MySQL (with PyMySQL connector)
- Libraries: pandas, pymysql, streamlit
# Dataset Overview
- Source: bus_data.csv
- Database: transport_db
- Table: bus_data
- Key fields:
• route_link
• busname
• bustype
• departing_time
• duration
• reaching_time
• star_rating
• price
• seats_available
• source_city
• destination_city
# Features Implemented
- Users can:
• Select source and destination cities
• Filter buses based on bus name, bus type, min & max price
• Filter by star rating and number of seats available
- Dynamic fetching of data using SQL queries from MySQL
- Real-time display of filtered results in tabular format
# Implementation Highlights
- Database Connection: Securely connected using pymysql
- Interactive UI: Built with Streamlit
- SQL Optimization: Dynamic query building using filters
- Error Handling: Connection and query-level errors handled
# Challenges Faced
- Initial connection issues due to MySQL credential errors
- Adjusted SQL queries to match actual database columns
- Set up MySQL CLI tools and environment on Windows
# Outcome
- Fully functional bus booking interface
- Responsive filtering of bus options
- Clean user interface backed by a database
Future Enhancements
- Add user login and booking system
- Integrate payment module
- Admin dashboard for bus management
- Map integration for routes
