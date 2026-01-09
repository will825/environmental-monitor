# Environmental Monitoring Station – Wiring Documentation

## Overview
This document describes the hardware wiring for the Environmental Monitoring Station
built using a Raspberry Pi and passive environmental sensors.

The system monitors:
- Temperature
- Humidity
- Ambient light level

All sensors operate at 3.3V logic level.

---

## Power Distribution
- Raspberry Pi Pin 1 (3.3V) → Breadboard positive rail
- Raspberry Pi Pin 6 (GND) → Breadboard ground rail

All sensors share a common ground.

---

## Sensors

### 1. DHT11 – Temperature & Humidity Sensor
Connections:
- VCC → 3.3V rail
- GND → GND rail
- DATA → GPIO4 (Physical Pin 7)

Purpose:
Measures ambient temperature and relative humidity.

---

### 2. Photoresistor (LDR) – Light Sensor
Configured as a voltage divider using a 10kΩ resistor.

Connections:
- One leg of photoresistor → 3.3V rail
- Other leg of photoresistor → junction point
- 10kΩ resistor from junction → GND rail
- Junction point → GPIO17 (Physical Pin 11)

Purpose:
Detects ambient light level (light vs dark).

---

## GPIO Summary Table

| Sensor | GPIO | Physical Pin |
|------|------|--------------|
| DHT11 DATA | GPIO4 | Pin 7 |
| Photoresistor Junction | GPIO17 | Pin 11 |

---

## Safety Notes
- Raspberry Pi must be powered off when modifying wiring.
- GPIO pins are used as inputs only.
- No 5V signals are connected to GPIO pins.
