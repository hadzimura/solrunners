# Springs of Life (2025)
# rkucera@gmail.com

from gpiozero import Button
# from gpiozero import DistanceSensor
# from gpiozero import LED
# from gpiozero import MotionSensor
from subprocess import check_call
from signal import pause

class RedButton(object):

    def __init__(self, pin_number):

        print("Initializing Red Button: '{}'".format(pin_number))
        self.red = Button(pin_number)


class Pir(object):

    def __init__(self, pin_number):

        print("Initializing PIR sensor: '{}'".format(pin_number))
        self.sensor = MotionSensor(pin_number)

class Led(object):

    def __init__(self, pin_number, color):
        print("Initializing LED diode ({}): '{}'".format(color, pin_number))
        self.light = LED(pin_number)




# class Sensor(object):
#
#     def __init__(self, pin_trigger=7, pin_echo=11, pin_pir=4):
#         self.pin_trigger = pin_trigger
#         self.pin_echo = pin_echo
#         self.pin_pir = pin_pir
#
#         self.pir = MotionSensor(self.pin_pir)
#         self.dist = DistanceSensor(echo=self.pin_echo, trigger=self.pin_trigger)

#
# class Distance(object):
#
#     """
#     https://gpiozero.readthedocs.io/en/latest/recipes.html#distance-sensor
#     """
#
#     def __init__(self, pin_trigger=7, pin_echo=11):
#
#         # GPIO.cleanup()
#         GPIO.setmode(GPIO.BOARD)
#         self.pin_trigger = pin_trigger
#         self.pin_echo = pin_echo
#
#         GPIO.setup(self.pin_trigger, GPIO.OUT)
#         GPIO.setup(self.pin_echo, GPIO.IN)
#         GPIO.output(self.pin_trigger, GPIO.LOW)
#
#         log.info('Setting up Motion Sensor HY SRF-05')
#         time.sleep(2)
#
#     def get_distance(self):
#
#         distance = 0
#
#         log.info('Sensor sensing')
#
#         try:
#             GPIO.output(self.pin_trigger, GPIO.HIGH)
#             time.sleep(0.00001)
#             GPIO.output(self.pin_trigger, GPIO.LOW)
#
#             pulse_start_time = 0
#             pulse_end_time = 0
#
#             while GPIO.input(self.pin_echo) == 0:
#                 pulse_start_time = time.time()
#
#             while GPIO.input(self.pin_echo) == 1:
#                 pulse_end_time = time.time()
#
#             pulse_duration = pulse_end_time - pulse_start_time
#             distance = round(pulse_duration * 17150, 2)
#             # log.info("Active distance: {} cm".format(distance))
#             # time.sleep(0.1)
#         except Exception as e:
#             log.error('Sensor said: {}'.format(e))
#
#         return distance
#
#     def shutdown(self):
#
#         GPIO.cleanup()


class Motion(object):

    """
    https://gpiozero.readthedocs.io/en/latest/recipes.html#motion-sensor
    """

    def __init__(self, pin_data=18):
        self.pir = MotionSensor(pin_data)

    def motion_function():
        print("Motion Detected")

    def no_motion_function():
        print("Motion stopped")
