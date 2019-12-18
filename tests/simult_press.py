import time

outer_switch = 5
inner_switch = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(outer_switch, GPIO.IN)
GPIO.setup(inner_switch, GPIO.IN)

button_delay = .5

while True:
    if GPIO.input(inner_switch) == 0:
        init_time = time.time()
        if GPIO.input(outer_switch) == 0 and time.time() - init_time == 250000000:
            print("Both")
    elif GPIO.input(outer_switch) == 0:
        