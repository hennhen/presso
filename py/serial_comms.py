import time
from enum import Enum
import struct
from typing import BinaryIO

import serial
import serial.tools.list_ports
from cobs import cobs

import sys

import robust_serial as rs
from robust_serial.utils import open_serial_port

ports = list(serial.tools.list_ports.comports())
arduino_port = None

zeroByte = b'\x00' # COBS 1-byte delimiter is hex zero as a (binary) bytes character
START_BYTE = b'\x02'

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
        # print(p)

        if "Arduino" in p.description:
            arduino_port = p.device
            break
    
    if arduino_port:
        arduino_serial = serial.Serial(port=arduino_port, baudrate=9600)
        if not arduino_serial.is_open:
                raise Exception("Failed to open serial connection to Arduino")
        print(f"Connected to: {p}")
    else:
        # No Arduino found before loop ends
        print(ports)
        raise Exception("No Arduino Found. Please check connection")

except Exception as e:
     print(f"Error: {e}")

buffer = bytearray()

while True:
    ## COBS ## 
    incoming_byte = arduino_serial.read(1)
    if incoming_byte == zeroByte:
        # read until the COBS packet ending delimiter is found
        str = arduino_serial.read_until( zeroByte ) 
        n = len(str)

        if n > 0:
            # take everything except the trailing zero byte, b'\x00'
            decodeStr = str[0:(n-1)]

            # recover binary data encoded on Arduino
            dataDecoded = cobs.decode( decodeStr ) 
            n_binary = len(dataDecoded)

            if (n_binary == 4):
                # floats in python from the Arduino
                num = struct.unpack('f',dataDecoded)
                print(num)

