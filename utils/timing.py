import ctypes, os


CLOCK_MONOTONIC_RAW = 4

class timespec(ctypes.Structure):
    _fields_ =\
    [
        ('tv_sec', ctypes.c_long),
        ('tv_nsec', ctypes.c_long)
    ]

librt = ctypes.CDLL('librt.so.1', use_errno=True)
clock_gettime = librt.clock_gettime

clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

def monotonic_time():
    "return a timestamp in seconds (sec)"
    t = timespec()

    if clock_gettime(CLOCK_MONOTONIC_RAW , ctypes.pointer(t)) != 0:
        errno_ = ctypes.get_errno()
        raise OSError(errno_, os.strerror(errno_))
    return t.tv_sec + t.tv_nsec*1e-9

def micros():
    "return a timestamp in microseconds (us)"
    return monotonic_time()*1e6

def millis():
    "return a timestamp in milliseconds (ms)"
    return monotonic_time()*1e3

def delay(delay_ms):
    "delay for delay_ms milliseconds (ms)"
    t_start = millis()
    while (millis() - t_start < delay_ms):
        pass
    return

def delayMicroseconds(delay_us):
    "delay for delay_us microseconds (us)"
    t_start = micros()
    while (micros() - t_start < delay_us):
        pass
    return