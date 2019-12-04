import threading
from time import sleep
import keyboard

def doit(stop_event, arg):
    while not stop_event.wait(0.1):
        print ("working on %s" % arg)
    print("Stopping as you wish.")

pill2kill = threading.Event()
tasks = ["task ONE", "task TWO", "task THREE"]

def thread_gen(pill2kill, tasks):
    for task in tasks:
        t = threading.Thread(target=doit, args=(pill2kill, task))
        yield t

threads = list(thread_gen(pill2kill, tasks))
for thread in threads:
    thread.start()
threads_running = True
while threads_running:
    if keyboard.is_pressed('esc'):
        pill2kill.set()
        for thread in threads:
            thread.join()
        threads_running = False
print("Done!")