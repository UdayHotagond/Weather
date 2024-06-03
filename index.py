from tkinter import *
import tkinter as tk
from geopy.geocoders import Nominatim
from tkinter import ttk, messagebox
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz
import sqlite3

root = Tk()
root.title("Weather App")
root.geometry("900x500+300+200")
root.resizable(False, False)

# Connect to SQLite database
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()

# Create table
cursor.execute('''CREATE TABLE IF NOT EXISTS weather (
                    id INTEGER PRIMARY KEY,
                    city TEXT,
                    condition TEXT,
                    description TEXT,
                    temp INTEGER,
                    pressure INTEGER,
                    humidity INTEGER,
                    wind REAL,
                    timestamp TEXT
                )''')
conn.commit()

def getWeather():
    city = textfield.get()
    
    try:
        geolocator = Nominatim(user_agent="geoapiExercise", timeout=10)
        location = geolocator.geocode(city)
        if not location:
            raise ValueError("City not found")

        obj = TimezoneFinder()
        result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
        
        home = pytz.timezone(result)
        local_time = datetime.now(home)
        current_time = local_time.strftime("%I:%M %p")
        clock.config(text=current_time)
        name.config(text="CURRENT WEATHER")

        # Weather API
        api = "https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=06c921750b9a82d8f5d1294e1586276f"
        json_data = requests.get(api).json()
        
        if json_data.get("cod") != 200:
            raise ValueError(json_data.get("message", "Error retrieving data"))

        condition = json_data['weather'][0]['main']
        description = json_data['weather'][0]['description']
        temp = int(json_data['main']['temp'] - 273.15)
        pressure = json_data['main']['pressure']
        humidity = json_data['main']['humidity']
        wind = json_data['wind']['speed']
        timestamp = local_time.strftime("%Y-%m-%d %H:%M:%S")

        n = Label(font=("arial", 30, "bold"))
        n.place(x=400, y=300)

        t.config(text=(temp, "°"))
        c.config(text=(condition, "|", "FEELS", "LIKE", temp, "°"))
        n.config(text=(city.upper()))

        w.config(text=wind)
        h.config(text=humidity)
        d.config(text=description)
        p.config(text=pressure)

        # Insert data into database
        cursor.execute("INSERT INTO weather (city, condition, description, temp, pressure, humidity, wind, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (city, condition, description, temp, pressure, humidity, wind, timestamp))
        conn.commit()

    except Exception as e:
        messagebox.showerror("Error", str(e))

def showHistory():
    cursor.execute("SELECT city, condition, temp, timestamp FROM weather ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    
    history_window = Toplevel(root)
    history_window.title("Search History")
    history_window.geometry("400x200+750+300")
    
    for i, row in enumerate(rows):
        city, condition, temp, timestamp = row
        history_label = Label(history_window, text=f"{i+1}. {city} - {condition}, {temp}°C at {timestamp}", font=("Arial", 12))
        history_label.pack()

# search box
Search_image = PhotoImage(file="C:/Users/Uday/Desktop/weather/search.png")
myimage = Label(image=Search_image)
myimage.place(x=20, y=20)

textfield = tk.Entry(root, justify="center", width=17, font=("poppins", 25, "bold"), bg="#404040", border=0, fg="white")
textfield.place(x=50, y=40)
textfield.focus()

Search_icon = PhotoImage(file="C:/Users/Uday/Desktop/weather/search_icon.png")
myimage = Button(image=Search_icon, borderwidth=0, cursor="hand2", bg="#404040", command=getWeather)
myimage.place(x=400, y=34)

# View History button
history_button = Button(root, text="View History", font=("Arial", 10), command=showHistory)
history_button.place(x=800, y=10)

# logo
Logo_image = PhotoImage(file="C:/Users/Uday/Desktop/weather/logo.png")
myimage = Button(image=Logo_image)
myimage.place(x=150, y=100)

# Bottom box
Frame_image = PhotoImage(file="C:/Users/Uday/Desktop/weather/box.png")
myimage = Button(image=Frame_image)
myimage.pack(padx=5, pady=5, side=BOTTOM)

# time
name = Label(root, font=("Arial", 15, "bold"))
name.place(x=30, y=100)

clock = Label(root, font=("Helvetica", 20))
clock.place(x=30, y=130)

# label
label1 = Label(root, text="WIND", font=("Helvetica", 15, 'bold'), fg="white", bg="#1ab5ef")
label1.place(x=120, y=400)

label2 = Label(root, text="HUMIDITY", font=("Helvetica", 15, 'bold'), fg="white", bg="#1ab5ef")
label2.place(x=225, y=400)

label3 = Label(root, text="DESCRIPTION", font=("Helvetica", 15, 'bold'), fg="white", bg="#1ab5ef")
label3.place(x=430, y=400)

label4 = Label(root, text="PRESSURE", font=("Helvetica", 15, 'bold'), fg="white", bg="#1ab5ef")
label4.place(x=650, y=400)

t = Label(font=("arial", 70, "bold"), fg="#ee666d")
t.place(x=400, y=150)
c = Label(font=("arial", 30, "bold"))
c.place(x=400, y=250)

w = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
w.place(x=120, y=430)
h = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
h.place(x=280, y=430)
d = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
d.place(x=450, y=430)
p = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
p.place(x=670, y=430)

root.mainloop()

# Close the database connection when the program ends
conn.close()
