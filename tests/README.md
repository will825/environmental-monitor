# Sensor Test Scripts

This directory contains individual test scripts for validating each
sensor used in the Environmental Monitoring Station.

Each test script is designed to:
- Test one sensor at a time
- Output raw sensor readings
- Confirm correct wiring and GPIO configuration

## Test Files

### test_dht11.py
Validates temperature and humidity readings from the DHT11 sensor.

### test_photoresistor.py
Validates light detection using a photoresistor configured as a voltage divider.

### test_all_sensors.py
Runs a combined test to verify all sensors operate together without conflict.

## Usage
Each test should be run independently during hardware bring-up
before integrating sensors into the main application.
