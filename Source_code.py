#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import csv


# In[ ]:


driver = webdriver.Chrome()


url_dic={
    'Andhra Pradesh':'https://www.redbus.in/online-booking/apsrtc',
    'Kerala':'https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile',
    'Telangana':'https://www.redbus.in/online-booking/tsrtc/?utm_source=rtchometile',
    'Goa':'https://www.redbus.in/online-booking/ktcl/?utm_source=rtchometile',
    'Himachal Pradesh':'https://www.redbus.in/online-booking/hrtc/?utm_source=rtchometile',
    'Assam':'https://www.redbus.in/online-booking/astc/?utm_source=rtchometile',
    'Chandigarh':'https://www.redbus.in/online-booking/chandigarh-transport-undertaking-ctu',
    'Punjab':'https://www.redbus.in/online-booking/pepsu/?utm_source=rtchometile',
    'Bihar':'https://www.redbus.in/online-booking/bihar-state-road-transport-corporation-bsrtc/?utm_source=rtchometile',
    'West Bengal':'https://www.redbus.in/online-booking/west-bengal-transport-corporation?utm_source=rtchometile',
    'Sowth Bengal':'https://www.redbus.in/online-booking/south-bengal-state-transport-corporation-sbstc/?utm_source=rtchometile',
    'Jammu Kashmir':'https://www.redbus.in/online-booking/jksrtc'
}

bus_data = []
try:
    for state, url in url_dic.items():
        driver.get(url)
        time.sleep(5)

        wait = WebDriverWait(driver, 10)
        page = 1

        all_routes = []
        
        while True:
            print(f"Processing page: {page}")
            try:
                nested_div = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[4]')))
                route_list = nested_div.find_elements(By.CLASS_NAME, 'route_link')  

                for route in route_list:
                    try:
                        link_element = route.find_element(By.TAG_NAME, 'a')
                        route_name = link_element.get_attribute('title')  
                        route_link = link_element.get_attribute('href')
                        all_routes.append((state, route_name, route_link))
                    except Exception as e:
                        print(f"Error extracting route data: {e}")

                page_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".DC_117_pageTabs")))

                if page >= len(page_buttons): 
                    print("Reached the last page.")
                    break

                next_button = page_buttons[page]
                driver.execute_script("arguments[0].click();", next_button)
                
                page+=1
                time.sleep(2)  

            except Exception as e:
                print(f"Error navigating data on page {page}: {e}")
                break

        for state, route_name, route_link in all_routes:
            try:
                driver.get(route_link)
                time.sleep(3)

                try:
                    view_buses_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".button")))
                    view_buses_button.click() 
                except Exception as e:
                            print(f"no govt busses for this route {e}")

                bus_details = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "bus-item")))
                
                for bus in bus_details:
                    try:
                        bus_name = bus.find_element(By.CLASS_NAME, "travels").text
                        bus_type = bus.find_element(By.CLASS_NAME, "bus-type").text
                        departure_time = bus.find_element(By.CLASS_NAME, "dp-time").text
                        duration = bus.find_element(By.CLASS_NAME, "dur").text
                        reaching_time = bus.find_element(By.CLASS_NAME, "bp-time").text
                        
                        try:
                            star_rating = bus.find_element(By.CSS_SELECTOR, ".rating-sec .rating span").text
                        except Exception:
                            star_rating  = "N/A"
                        
                        fare = bus.find_element(By.CLASS_NAME, "fare").text.split()[-1]  # Extract numeric fare
       
                        try:
                            seats_available = bus.find_element(By.CLASS_NAME, "seat-left").text.split()[0]
                        except Exception:
                            seats_available = "N/A"

                        bus_data.append({
                            "state": state,
                            "route_name": route_name,
                            "route_link": route_link,
                            "busname": bus_name,
                            "bustype": bus_type,
                            "departing_time": departure_time,
                            "duration": duration,
                            "reaching_time": reaching_time,
                            "star_rating": star_rating,
                            "price": fare,
                            "seats_available": seats_available
                            })
                    except:
                        pass

            except:
                pass

    with open("bus_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "state", "route_name", "route_link", "busname", "bustype",
            "departing_time", "duration", "reaching_time", "star_rating", "price", "seats_available"
        ])
        writer.writeheader()
        writer.writerows(bus_data)
finally:
    driver.quit()


# In[ ]:


import pandas as pd
data = pd.read_csv("bus_data.csv")

data['departing_time'] = pd.to_datetime(data['departing_time'], format='%H:%M', errors='coerce').dt.time
data['reaching_time'] = pd.to_datetime(data['reaching_time'], format='%H:%M', errors='coerce').dt.time

if 'route_name' in data.columns:
        split_routes = data['route_name'].str.split(' to ', n=1, expand=True)
        data['from_city'] = split_routes[0].str.strip()
        data['to_city'] = split_routes[1].str.strip() if split_routes.shape[1] > 1 else None

print(data.head())


# In[ ]:


data.dropna(inplace=True)


# In[ ]:


import pymysql

mydb = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="bishh1310",  # Update with your database password
            database = "transport_db" 
        )
mycursor = mydb.cursor()


# In[ ]:


mycursor.execute("""CREATE TABLE bus_data (
    state VARCHAR(100),from_city VARCHAR(100),to_city VARCHAR(100),
    route_name VARCHAR(255),
    route_link TEXT,
    busname VARCHAR(255),
    bustype VARCHAR(255),
    departing_time TEXT,
    duration VARCHAR(50),
    reaching_time text,
    star_rating DECIMAL(2,1),
    price DECIMAL(10,2),
    seats_available INT
);""")
mydb.commit()


# In[ ]:


data.columns


# In[ ]:


for i,row in data.iterrows():
    insert_query = """insert into bus_data(state,route_name,route_link,busname,bustype,departing_time,duration,reaching_time,
                       star_rating,price,seats_available,from_city, to_city)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    values = (row['state'],row['route_name'],row['route_link'],row['busname'],row['bustype'],row['departing_time'],row['duration'],
              row['reaching_time'],row['star_rating'],row['price'],row['seats_available'],row['from_city'],row['to_city'])
    mycursor.execute(insert_query,values)
    mydb.commit()


# In[ ]:


data['bustype'].unique()

