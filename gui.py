import PySimpleGUI as sg
from aquarium_controller import AquariumController
import sys
import os
import json
import logging


class GUI:

    @staticmethod
    def get_path(filename):
        if hasattr(sys, "_MEIPASS"):
            return f'{os.path.join(sys._MEIPASS, filename)}'
        else:
            return f'{filename}'

    @staticmethod
    def get_initial_scheduler_values():
        json_file = open("lights_plan.json")
        data = json.load(json_file)
        json_file.close()
        return data['scheduler']

    def run(self):
        FONT = 'Consolas 9'
        FONT_BUTTONS = 'Consolas 12'
        sg.theme('BlueMono')
        init_values = self.get_initial_scheduler_values()
        layout = [
            [sg.Frame(title='Day lights', element_justification='center', font='Consolas 9', size=(100, 65),
                      layout=[[sg.Image(filename=self.get_path('red_status.png'), key='_DAY_STATUS_')]]),
             sg.Frame(title='Night lights', element_justification='center', font='Consolas 9', size=(100, 65),
                      layout=[[sg.Image(filename=self.get_path('red_status.png'), key='_NIGHT_STATUS_',)]]),
             sg.Frame(title='Temperature', element_justification='center', font='Consolas 9', size=(100, 65),
                      layout=[[sg.Text('00°C', font='Consolas 25', key='_TEMPERATURE_')]])],
            [sg.Column([
                [sg.Text('Day lights time on:', font=FONT, size=24),
                 sg.InputText(default_text=init_values["DAY_LIGHTS_TIME_ON"], key='_DAY_LIGHTS_TIME_ON_', size=(2, 1)),
                sg.Text('Day lights time off:', font=FONT, size=24),
                 sg.InputText(default_text=init_values["DAY_LIGHTS_TIME_OFF"], key='_DAY_LIGHTS_TIME_OFF_', size=(2, 1))],
                [sg.Text('Night lights time on 1:', font=FONT, size=24),
                 sg.InputText(default_text=init_values["NIGHT_LIGHTS_TIME_ON_1"], key='_NIGHT_LIGHTS_TIME_ON_1_', size=(2, 1)),
                sg.Text('Night lights time off 1:', font=FONT, size=24),
                 sg.InputText(default_text=init_values["NIGHT_LIGHTS_TIME_OFF_1"], key='_NIGHT_LIGHTS_TIME_OFF_1_', size=(2, 1))],
                [sg.Text('Night lights time on 2:', font=FONT, size=24),
                 sg.InputText(default_text=init_values["NIGHT_LIGHTS_TIME_ON_2"], key='_NIGHT_LIGHTS_TIME_ON_2_', size=(2, 1)),
                sg.Text('Night lights time off 2:', font=FONT, size=24),
                 sg.InputText(default_text=init_values["NIGHT_LIGHTS_TIME_OFF_2"], key='_NIGHT_LIGHTS_TIME_OFF_2_', size=(2, 1))],
            ]), sg.Column([[sg.Submit(key='_UPDATE_', font=FONT_BUTTONS, button_text='Update')]])],
            [sg.Output(size=(85, 10), font=FONT, key='_OUTPUT_')],
            [sg.Exit(font=FONT_BUTTONS)]
        ]

        window = sg.Window('Aquarium controller tool', layout)

        thread = None

        while True:
            try:
                event, values = window.read(timeout=100)
                if event in (None, 'Exit'):
                    thread.lights_controller.set_init_gpio()
                    break
                elif not thread:
                    thread = AquariumController()
                if thread:
                    if thread.lights_controller.DAY_LIGHT_ON:
                        window.Element('_DAY_STATUS_').update(filename=self.get_path('green_status.png'))
                    else:
                        window.Element('_DAY_STATUS_').update(filename=self.get_path('red_status.png'))
                    if thread.lights_controller.NIGHT_LIGHT_ON:
                        window.Element('_NIGHT_STATUS_').update(filename=self.get_path('green_status.png'))
                    else:
                        window.Element('_NIGHT_STATUS_').update(filename=self.get_path('red_status.png'))
                    window.Element('_TEMPERATURE_').update(f'{thread.temperature_sensor.TEMPERATURE}°C')
                    if thread.temperature_sensor.ALARM:
                        window.Element('_TEMPERATURE_').update(f'{thread.temperature_sensor.TEMPERATURE}°C',
                                                               text_color='red')
                    else:
                        window.Element('_TEMPERATURE_').update(f'{thread.temperature_sensor.TEMPERATURE}°C',
                                                               text_color='black')
                if event == "_UPDATE_":
                    with open(self.get_path('lights_plan.json'), 'r+') as json_file:
                        data = json.load(json_file)
                        data['scheduler']['DAY_LIGHTS_TIME_ON'] = values['_DAY_LIGHTS_TIME_ON_']
                        data['scheduler']['DAY_LIGHTS_TIME_OFF'] = values['_DAY_LIGHTS_TIME_OFF_']
                        data['scheduler']['NIGHT_LIGHTS_TIME_ON_1'] = values['_NIGHT_LIGHTS_TIME_ON_1_']
                        data['scheduler']['NIGHT_LIGHTS_TIME_ON_2'] = values['_NIGHT_LIGHTS_TIME_ON_2_']
                        data['scheduler']['NIGHT_LIGHTS_TIME_OFF_1'] = values['_NIGHT_LIGHTS_TIME_OFF_1_']
                        data['scheduler']['NIGHT_LIGHTS_TIME_OFF_2'] = values['_NIGHT_LIGHTS_TIME_OFF_2_']
                        json_file.seek(0)
                        json.dump(data, json_file, indent=4)
                        json_file.truncate()
                    thread.lights_controller.refresh()
            except Exception as e:
                logging.warning(f'Somethings is fucked up: {e}')
        window.close()


if __name__ == '__main__':
    GUI().run()