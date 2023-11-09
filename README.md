# Weather Display

## Description

This is a simple consol application to display weather information from
a weather station and Open Weather Map. To use this you'll need to put your api
key in a .env file as well as the address of your weather stations MQTT server

## Configuration
Below is what needs to be in a .env file in the same location as the source
code:
``` 
WEATHER_API_KEY="<YOUR OPEN WEATHER MAP API KEY>"
WEATHER_LATITUDE=<YOUR LATITUDE>
WEATHER_LONGITUDE= <YOUR LONGITUDE>
WEATHER_MQTT_SERVER="<YOUR WEATHER STAION'S ADDRESS>"
```
