import datetime
import json
import logging

import RPi.GPIO as GPIO


class LightsController:

    def __init__(self, day_lights_pin_ac, day_lights_pin_dc, night_lights_pin):

        self.day_lights_pin_ac = day_lights_pin_ac
        self.day_lights_pin_dc = day_lights_pin_dc
        self.night_lights_pin = night_lights_pin
        GPIO.setup(self.day_lights_pin_ac, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.day_lights_pin_dc, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.night_lights_pin, GPIO.OUT, initial=GPIO.HIGH)

        self.lights_plan = self.get_lights_plan()
        self.dirty_light_list = self.get_dirty_list_for_night_scheduler()
        self.DAY_LIGHT_ON = False
        self.NIGHT_LIGHT_ON = False
        self.counter = 0

    def refresh(self):
        self.lights_plan = self.get_lights_plan()
        self.dirty_light_list = self.get_dirty_list_for_night_scheduler()

    @staticmethod
    def get_lights_plan():
        scheduler = {}
        with open('lights_plan.json') as json_file:
            data = json.load(json_file)['scheduler']
            scheduler = {'day_light_time_on': int(data['DAY_LIGHTS_TIME_ON']),
                         'day_light_time_off': int(data['DAY_LIGHTS_TIME_OFF']),
                         'night_light_time_on_1': int(data['NIGHT_LIGHTS_TIME_ON_1']),
                         'night_light_time_on_2': int(data['NIGHT_LIGHTS_TIME_ON_2']),
                         'night_light_time_off_1': int(data['NIGHT_LIGHTS_TIME_OFF_1']),
                         'night_light_time_off_2': int(data['NIGHT_LIGHTS_TIME_OFF_2'])}
        return scheduler

    def get_dirty_list_for_night_scheduler(self):
        hours_list = []
        for hour in range(self.lights_plan['night_light_time_on_1'], self.lights_plan['night_light_time_off_1']):
            hours_list.append(hour)
        night_time_off_2 = self.lights_plan['night_light_time_off_2'] if self.lights_plan['night_light_time_off_2'] != 0 else 24
        for hour in range(self.lights_plan['night_light_time_on_2'], night_time_off_2):
            hours_list.append(hour)
        return hours_list

    @staticmethod
    def get_hour():
        return datetime.datetime.now().hour
        # self.counter += 1
        # if self.counter > 23:
        #     self.counter = 0
        # print(f"Godzina: {self.counter}")
        # return self.counter

    @staticmethod
    def turn_lights_on(pin):
        GPIO.output(pin, GPIO.LOW)
        # pass

    @staticmethod
    def turn_lights_off(pin):
        GPIO.output(pin, GPIO.HIGH)
        # pass

    def check_scheduler(self):
        hour = self.get_hour()
        if self.lights_plan['day_light_time_on'] <= hour < self.lights_plan['day_light_time_off'] and not self.DAY_LIGHT_ON:
            self.turn_lights_on(self.day_lights_pin_ac)
            self.turn_lights_on(self.day_lights_pin_dc)
            self.DAY_LIGHT_ON = True
            logging.info('Turning on day lights')
        if self.lights_plan['day_light_time_off'] <= hour and self.DAY_LIGHT_ON:
            self.turn_lights_off(self.day_lights_pin_ac)
            self.turn_lights_off(self.day_lights_pin_dc)
            self.DAY_LIGHT_ON = False
            logging.info('Turning off day lights')
        if hour in self.dirty_light_list and not self.NIGHT_LIGHT_ON and not self.DAY_LIGHT_ON:
            self.turn_lights_on(self.night_lights_pin)
            self.NIGHT_LIGHT_ON = True
            logging.info('Turning on night lights')
        if hour not in self.dirty_light_list and self.NIGHT_LIGHT_ON:
            self.turn_lights_off(self.night_lights_pin)
            self.NIGHT_LIGHT_ON = False
            logging.info('Turning off night lights')
