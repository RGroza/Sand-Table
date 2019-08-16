import threading
from time import sleep

def doit(stop_event, arg):
    while not stop_event.wait(1):
        print ("working on %s" % arg)
    print("Stopping as you wish.")

pill2kill = threading.Event()
try:
    tasks = ["task ONE", "task TWO", "task THREE"]

    def thread_gen(pill2kill, tasks):
        for task in tasks:
            t = threading.Thread(target=doit, args=(pill2kill, task))
            yield t

    threads = list(thread_gen(pill2kill, tasks))
    for thread in threads:
        thread.start()
except KeyboardInterrupt:
    pill2kill.set()
    for thread in threads:
        thread.join()