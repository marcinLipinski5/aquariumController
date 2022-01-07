import logging
import RPi.GPIO as GPIO
from lights_controller import LightsController
from temperature_sensor import TemperatureSensor
import time
import threading


class AquariumController:

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("aquarium_log.log"),
                logging.StreamHandler()
            ]
        )

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.lights_controller = LightsController(day_lights_pin_ac=2,
                                                  day_lights_pin_dc=3,
                                                  night_lights_pin=4)
        self.temperature_sensor = TemperatureSensor()
        self.thread = threading.Thread(target=self.aquarium_loop, args=(), daemon=True)
        self.thread.start()

    def aquarium_loop(self):
        while True:
            try:
                self.lights_controller.check_scheduler()
                self.temperature_sensor.check_temperature()
                time.sleep(1)
            except Exception as e:
                logging.warning(f'Something failed: {e}')


if __name__ == "__main__":
    AquariumController()
