from datetime import datetime
import json
from time import sleep
from queue import Queue
from threading import Thread
import paho.mqtt.client as mqtt
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.box import ROUNDED, Box
import requests
from decouple import config

console = Console()
msg_queue = Queue()
conditions_queue = Queue()
forecast_queue = Queue()
weather_api_key = config('WEATHER_API_KEY')
latitude = config('WEATHER_LATITUDE')
longitude = config('WEATHER_LONGITUDE')
forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?units=metric&lat=-{latitude}&lon={longitude}&appid={weather_api_key}"
current_conditions_url = f"https://api.openweathermap.org/data/2.5/weather?units=metric&lat={latitude}&lon={longitude}&appid={weather_api_key}"

def get_json(url):
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return None

class QueueData:
    def __init__(self, in_q):
        self.last_data = {}
        self.in_q = in_q

    def get_data(self):
        try:
            self.last_data = self.in_q.get(block=False)
        except:
            return self.last_data

class Forecast:
   def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        for forcast in data.list:
            dt_utc = datetime.fromtimestamp(forcast.dt)
            grid.add_row("min", forcast.main.temp_min)
            grid.add_row("max", forcast.main.temp_max)

class CurrentConditions:
   _queue_data = QueueData(conditions_queue)

   def __rich__(self) -> Panel:
        data = CurrentConditions._queue_data.get_data()
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        if data:
            for key, val in data.items():
                grid.add_row(key, val)
        #if data:
        #    grid.add_row("max", data["main"]["temp_max"])
        #    grid.add_row("min", data["main"]["temp_min"])
        return Panel(grid, style="white on blue")

def make_layout() -> Layout:
    layout = Layout(name="root")
    layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            )
    layout["body"].split_row(
            Layout(name="Forecast"),
            Layout(name="Current"))
    return layout

class Header:
    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row("Weather", datetime.now().ctime())
        return Panel(grid, style="white on blue")


def _get_as_float(d):
    try:
        return float(d)
    except ValueError:
        pass
    return None



class WeatherStation:
    _queue_data = QueueData(msg_queue)
    def __rich__(self) -> Panel:
        try:
            data = WeatherStation._queue_data.get_data()
            grid = Table.grid(expand=True)
            grid.add_column(justify="center", ratio=1)
            grid.add_column(justify="center")
            for key, val in data.items():
                grid.add_row(key, val)
            return Panel(grid, style="white on blue")
        except:
            grid = Table.grid(expand=True)
            return Panel(grid)
        return panel

def on_connect(client, userdata, flags, rc):
    client.subscribe("weather/all")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode("utf-8"))
    userdata["message_q"].put(data)

def read_mqqt(out_q):
    client_data = {"message_q": out_q}
    client = mqtt.Client("display_client", userdata=client_data)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("raspberrypi.local", 1883, 60)
    client.loop_start()

def read_current_conditions(out_q):
    data = get_json(current_conditions_url)
    if data:
        out_q.put(data)
    else:
        out_q.put({"temp_min": -3423})

def read_forecast(out_q):
    while True:
        data = get_json(forecast_url)
        if data:
            out_q.put(data)
        sleep(3600)

def main():
    t1 = Thread(target=read_mqqt, args=(msg_queue,), daemon=True)
    t1.start()
    #read_current_conditions(conditions_queue)
    #t2.start()
    layout = make_layout()
    layout["header"].update(Header())
    layout["Current"].update(WeatherStation())
    layout["Forecast"].update(CurrentConditions())
    with Live(layout, refresh_per_second=10, screen=True):
        while True:
            # data = msg_queue.get()
            sleep(2)

if __name__ == "__main__":
    main()
