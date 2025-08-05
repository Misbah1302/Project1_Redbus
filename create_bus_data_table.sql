
CREATE DATABASE IF NOT EXISTS transport_db;

USE transport_db;

CREATE TABLE IF NOT EXISTS bus_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    route_name VARCHAR(255),
    route_link TEXT,
    busname VARCHAR(100),
    bustype VARCHAR(100),
    departing_time VARCHAR(10),
    duration VARCHAR(20),
    reaching_time VARCHAR(10),
    star_rating FLOAT,
    price FLOAT,
    seats_available INT
);
