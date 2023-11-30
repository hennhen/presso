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
        arduino_serial = serial.Serial(port=arduino_port, baudrate=115200, timeout=None)
        if not arduino_serial.is_open:
                raise Exception("Failed to open serial connection to Arduino")
        print(f"Connected to: {p}")
    else:
        # No Arduino found before loop ends
        print(ports)
        raise Exception("No Arduino Found. Please check connection")

except Exception as e:
     print(f"Error: {e}")

arduino_serial.reset_input_buffer()
arduino_serial.reset_output_buffer()

buffer = bytearray()

SET_MOTOR_SPEED = 0x04

command = struct.pack("<hf", 4, 4.7321)
print(len(command))
command_encoded = cobs.encode(command) 
print(len(command_encoded))

# Wait for Arduino to wake up
time.sleep(3)

while True:
    num_of_outgoing_bytes = arduino_serial.write(command_encoded + b'\x00')
    print( "python wrote {0} bytes. command_encoded: {1}".format(num_of_outgoing_bytes, command_encoded))

    ## COBS ## 
    incoming_bytes = arduino_serial.read_until( zeroByte )
    print(incoming_bytes)

    # take everything except the trailing zero byte, b'\x00'
    n_incoming_bytes = len(incoming_bytes)
    data_raw = incoming_bytes[0:(n_incoming_bytes-1)]

    # recover binary data encoded on Arduino
    data_decoded = cobs.decode( data_raw ) 
    n_data_decoded = len(data_decoded)

    print(data_decoded)

    if (n_data_decoded == 4):
        # floats in python from the Arduino
        num = struct.unpack('f',data_decoded)
        print(num)
    time.sleep(1)