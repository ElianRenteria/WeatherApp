import tkinter as tk
from PIL import Image, ImageTk
import requests
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from apiKey import key


global t
t = 0


def get_day_or_night(city_name):
    def is_daytime(current_time, sunrise, sunset):
        return sunrise <= current_time <= sunset

    # Use geopy to get the latitude and longitude of the city
    geolocator = Nominatim(user_agent="city_time_app")
    location = geolocator.geocode(city_name)

    if location:
        latitude, longitude = location.latitude, location.longitude

        # Use the timezonefinder library to get the timezone based on latitude and longitude
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)

        # Use the timezone information from pytz
        timezone = pytz.timezone(timezone_str)

        # Get the current time in the specified timezone
        current_time = datetime.now(timezone)

        # Check if 'sunrise' key is present in the raw data
        if 'sunrise' in location.raw:
            sunrise = datetime.fromtimestamp(location.raw['sunrise'], timezone)
            sunset = datetime.fromtimestamp(location.raw['sunset'], timezone)

            if is_daytime(current_time, sunrise, sunset):
                return True
            else:
                return False
        else:
            return "Sunrise/sunset data not available for this location."
    else:
        return "Could not find location information for the city."


def on_entry_click(event):
    if city.get() == "Enter city":
        city.delete(0, "end")  # Remove the default placeholder text
        city.config(fg="black")  # Change text color to black

def on_focus_out(event):
    if not city.get():
        city.insert(0, "Enter city")  # Add back the placeholder text
        city.config(fg="grey")  # Change text color to grey
        
        
        
def getWeather(location):
    global t
    city = location
    api_url = 'https://api.api-ninjas.com/v1/weather?city={}'.format(city)
    response = requests.get(api_url, headers={'X-Api-Key': key})
    if response.status_code == requests.codes.ok:
        #print(response.text)
        t = response.json()['temp']
        t = t*9/5+32
        temp.config(text="{}°C".format(response.json()['temp']))
        maxTemp.config(text="Max: {}°C".format(response.json()['max_temp']))
        minTemp.config(text="Min: {}°C".format(response.json()['min_temp']))
        humidity.config(text="Humidity: {}%".format(response.json()['humidity']))
        windSpeed.config(text="Wind: {} mph".format(response.json()['wind_speed']))
        # set icon
        if not get_day_or_night(location):
            image = Image.open("assets/night.png")
            resized_image = image.resize((300,300), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(resized_image)
            imageLabel.configure(image=photo)
            imageLabel.image = photo
        elif response.json()['cloud_pct'] > 70:
            if get_day_or_night(location):
                image = Image.open("assets/cloudynight.png")
                resized_image = image.resize((300,300), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(resized_image)
                imageLabel.configure(image=photo)
                imageLabel.image = photo
            else:
                image = Image.open("assets/cloud.png")
                resized_image = image.resize((300,300), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(resized_image)
                imageLabel.configure(image=photo)
                imageLabel.image = photo
        elif 20 <= response.json()['cloud_pct']  <= 70 and response.json()['temp']  < 15:
            image = Image.open("assets/cloudynight.png") 
            resized_image = image.resize((300,300), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(resized_image)
            imageLabel.configure(image=photo)
            imageLabel.image = photo
        elif response.json()['temp']  >= 15:
            image = Image.open("assets/sunny.png") 
            resized_image = image.resize((300,300), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(resized_image)
            imageLabel.configure(image=photo)
            imageLabel.image = photo
        window.update()
    else:
        print("Error:", response.status_code, response.text)


# Create a window
window = tk.Tk()

# Set the title
window.title("Weather App")

# Set the window size
window.geometry("500x600")

# Set the background color
window.configure(bg="white")
window.resizable(False, False)


# create frame for wather icon
imageFrame = tk.Frame(window, width=300, height=300)
imageFrame.place(x=100, y=50)
imageLabel = tk.Label(imageFrame, background="grey",height=300,width=300)
imageLabel.place(x=0, y=0)

# create frame for input
inputFrame = tk.Frame(window, bg="",width=400, height=60)
inputFrame.place(x=50, y=500)
city = tk.Entry(inputFrame, width=10,background="white",font=("Arial", 42),fg="grey", insertofftime=0, insertontime=0)
city.insert(0, "Enter city")  # Add the placeholder text initially
city.bind("<FocusIn>", on_entry_click)
city.bind("<FocusOut>", on_focus_out)
city.pack(side=tk.LEFT)
submit = tk.Button(inputFrame, text="Enter",background="#00FF00",font=("Arial", 18),height=2,width=5,activebackground="#228B22",command=lambda: getWeather(city.get()))
submit.pack()
# create frame for weather data
dataFrame = tk.Frame(window,width=400, height=120,background="white")
dataFrame.place(x=50, y=360)
#temp
tempFrame = tk.Frame(dataFrame,width=200, height=120)
tempFrame.pack(side=tk.LEFT)
temp = tk.Label(tempFrame, text="{}°C".format(t),font=("Arial", 46),width=6, background="white")
temp.pack()
#other data
otherFrame = tk.Frame(dataFrame,width=200, height=120)
otherFrame.pack(side=tk.RIGHT)
maxTemp = tk.Label(otherFrame, text="Max: ",font=("Arial", 18),width=16,anchor="w",fg="grey",background="white")
maxTemp.pack(side=tk.TOP)
minTemp = tk.Label(otherFrame, text="Min: ",font=("Arial", 18),width=16,anchor="w",fg="grey",background="white")
minTemp.pack()
humidity = tk.Label(otherFrame, text="Humidity: ",font=("Arial", 18),width=16,anchor="w",fg="grey",background="white")
humidity.pack()
windSpeed = tk.Label(otherFrame, text="Wind: ",font=("Arial", 18),width=16,anchor="w",fg="grey",background="white")
windSpeed.pack()




# Create a label
window.mainloop()

