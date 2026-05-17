from gpiozero import MotionSensor
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

# Suppress warnings
GPIO.setwarnings(False)

pir = MotionSensor(16)

while True:
    pir.wait_for_motion()
    print('Motion detected')
    pir.wait_for_motion()
    print('movement ceased')
