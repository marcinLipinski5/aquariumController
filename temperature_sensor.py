import os

# import RPi.GPIO as GPIO
# import w1thermsensor
import logging
import random

class TemperatureSensor:

    def __init__(self):
        # GPIO.setup(6, GPIO.OUT, initial=GPIO.LOW)

        self.temperature_max = os.getenv('TEMPERATURE_MAX', 24.0)
        # self.sensor = w1thermsensor.W1ThermSensor()
        self.TEMPERATURE = 0
        self.ALARM = False

    def check_temperature(self):
        temperature = random.randint(22, 23)
        # temperature = self.sensor.get_temperature()
        if temperature > self.temperature_max:
            # GPIO.output(21, GPIO.HIGH)
            self.ALARM = True
            logging.warning('!!Temperature is to high!!!')
        else:
            pass
            self.ALARM = False
            # GPIO.output(21, GPIO.LOW)
        self.TEMPERATURE = temperature
