"""
DHT11 test script
Reads temperature and humidity and prints them to the terminal.
"""


import time
import board
import adafruit_dht

dht_sensor = adafruit_dht.DHT11(board.D4)
try:
 
    temperature =  dht_sensor.temperature
    temperature_f = (temperature * 9 / 5) + 32

    humidity = dht_sensor.humidity
    print(f"Temp: {temperature_f} F, Humidity: {humidity} %") 
except RuntimeError as error:
    print(f"Reading error: {error}")
finally: dht_sensor.exit()
