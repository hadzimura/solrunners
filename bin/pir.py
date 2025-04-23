from gpiozero import MotionSensor

pir = MotionSensor(16)

while True:
    pir.wait_for_motion()
    print('Motion detected')
    pir.wait_for_motion()
    print('movement ceased')
