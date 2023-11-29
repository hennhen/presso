import time
from enum import Enum
import struct
from typing import BinaryIO

import serial
import serial.tools.list_ports

import sys
print("Python interpreter:", sys.executable)


import robust_serial as rs
from robust_serial.utils import open_serial_port

ports = list(serial.tools.list_ports.comports())
arduino_port = None
# s = None

class Order(Enum):
    """
    Pre-defined orders
    """
    HELLO = 0
    MOTOR = 1
    SPEED = 2
    PRESSURE_SETPOINT = 3
    PID_P = 4
    PID_I = 5
    PID_D = 6
    STOP = 7

    FEEDBACK_PRESSURE = 8
    FEEDBACK_PWM = 9
    FEEDBACK_SPEED = 10

try:
    for p in ports:
        print(p)

        if "Arduino" in p.description:
            arduino_port = p.device
            break
    
    if arduino_port:
        arduino_serial = rs.utils.open_serial_port(baudrate=9600, timeout=None)
        if not arduino_serial.is_open:
                raise Exception("Failed to open serial connection to Arduino")
        print(f"Connected to: {p}")
    else:
        # No Arduino found before loop ends
        print(ports)
        raise Exception("No Arduino Found. Please check connection")

except Exception as e:
     print(f"Error: {e}")


while(True):
    rs.write_order(arduino_serial, Order.MOTOR)
    rs.write_i8(arduino_serial, 9)
    time.sleep(100)