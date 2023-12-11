import time
from enum import Enum
import struct
from typing import BinaryIO

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime as dt

import serial
import serial.tools.list_ports
from cobs import cobs

import sys

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

import robust_serial as rs
from robust_serial.utils import open_serial_port

ports = list(serial.tools.list_ports.comports())
arduino_port = None

zeroByte = b'\x00' # COBS 1-byte delimiter is hex zero as a (binary) bytes character

class Command(Enum):
    """ Enum for command types """
    SET_MOTOR_SPEED = 1
    SET_PID_VALUES = 2
    SET_PRESSURE = 3
    STOP = 4

    TARGET_PRESSURE = 6
    WEIGHT_READING = 7
    EXTRACTION_STOPPED = 8
    PRESSURE_READING = 9

""" Command Packet Creators """
def create_pid_packet(p, i, d, setpoint, targetWeight=0):
    # SUPER IMPORTANT
    packet = struct.pack('<hfffff', Command.SET_PID_VALUES.value, p, i, d, setpoint, targetWeight)
    encoded_packet = cobs.encode(packet) + b'\x00'
    return encoded_packet

def create_motor_speed_packet(speed):
    packet = struct.pack('<hf', Command.SET_MOTOR_SPEED.value, speed)
    encoded_packet = cobs.encode(packet) + b'\x00'
    return encoded_packet

def create_stop_packet():
    packet = struct.pack('<h', Command.STOP.value)
    encoded_packet = cobs.encode(packet) + b'\x00'
    return encoded_packet

def receive_command(serial_conn):
    try:
        incoming_bytes = serial_conn.read_until(zeroByte)
        if len(incoming_bytes) < 2:  # At least 2 bytes (for a short command)
            print("Packet < 2")
            return None, None
    except KeyboardInterrupt:
        print("Keyboard Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(0)

    data_raw = incoming_bytes[:-1]  # Exclude the trailing zero byte

    try:
        data_decoded = cobs.decode(data_raw)
    except cobs.DecodeError:
        print("COBS Decode Error")
        # ignore this packet
        return None, None
    
    if len(data_decoded) >= 2:  # At least 2 bytes for command
        command = struct.unpack('<h', data_decoded[:2])[0]

        if command == Command.EXTRACTION_STOPPED.value:
            return command, None
        elif command == Command.PRESSURE_READING.value and len(data_decoded) == 6:  # command + float
            pressure_value = struct.unpack('<f', data_decoded[2:])[0]
            return command, pressure_value
        elif command == Command.WEIGHT_READING.value and len(data_decoded) == 6:  # New condition for weight command
            weight_value = struct.unpack('<f', data_decoded[2:])[0]
            return command, weight_value
        elif command == Command.TARGET_PRESSURE.value and len(data_decoded) == 6:
            target_pressure_value = struct.unpack('<f', data_decoded[2:])[0]
            return command, target_pressure_value
    
    return None, None

## PLOTTING STUFF ##
# Global lists to store time and pressure data
pressure_data = []
weight_data = []
target_pressure = []

def start_plotting(p, i, d, setpoint, targetWeight, packet):
    global app, win, pressure_plot, weight_plot, pressure_curve, weight_curve, target_pressure, target_pressure_curve, timer

    # PyQtGraph plotting setup
    app = QApplication([])

    # Create the main window with a grid layout
    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle('Real-time Pressure and Weight Plots')

    # Resize the window to a bigger size
    win.resize(800, 600)
    label = win.addLabel(
    f'<div style="text-align: center; vertical-align: middle; line-height: normal;">'
    f'<span style="font-size: 18pt; text-align: center;">kP: 700, kI: 5.5, kD: 0, Sample Time: 1 ms</span><br>'
    f'<span style="font-size: 18pt; text-align: center;">Duration: 5s</span><br>'
    f'</div>', 
    row=0, col=0, colspan=1
)

    
    # Add the plot for pressure and target pressure
    pressure_plot = win.addPlot(title="Pressure Plot", row=1, col=0, colspan=1)
    pressure_plot.setYRange(0, 12)  # Set y range for pressure plot
    pressure_plot.setLabel('left', 'Pressure', units='bars', size=50)
    pressure_curve = pressure_plot.plot(pen='y')
    target_pressure_curve = pressure_plot.plot(pen='g')  # Add target pressure curve
    
    # Next row for weight plot
    # win.nextRow()
    # weight_plot = win.addPlot(title="Weight Plot")
    # weight_plot.setYRange(0, 15)  # Set y range for weight plot
    # weight_curve = weight_plot.plot(pen='r')
    # weight_plot.addLine(y=targetWeight, pen='g')  # Set horizontal line for weight setpoint

    # Configure the timer to read data
    timer = QTimer()
    timer.timeout.connect(read_serial_data)
    timer.start(0)  # Adjust as necessary for your data rate

    # Start the PyQtGraph application
    app.exec_()
    

def read_serial_data():
    global pressure_data, weight_data, target_pressure, pressure_plot, weight_plot, pressure_curve, weight_curve, target_pressure_curve, timer, arduino_serial
    command, value = receive_command(arduino_serial)
    # print("Recieved Command: {0}, Value: {1}".format(command, value))

    if command is not None:
        if command == Command.EXTRACTION_STOPPED.value:
            # print("Extraction Stopped.")
            pass
        elif command == Command.PRESSURE_READING.value:
            # print(f"Pressure Reading: {value}")
            pressure_data.append(value)  # Append only the pressure value
            update_pressure_plot()  # Update the plot
        elif command == Command.TARGET_PRESSURE.value:
            # print(f"Target Pressure: {value}")
            target_pressure.append(value)  # Append only the pressure value
            update_target_pressure_plot()  # Update the plot
        elif command == Command.WEIGHT_READING.value:
            # print(f"Weight Reading: {value}")
            weight_data.append(value)
            update_weight_plot()

def update_pressure_plot():
    global pressure_data
    pressure_curve.setData(pressure_data)

def update_weight_plot():
    global weight_data
    weight_curve.setData(weight_data)

def update_target_pressure_plot():
    global target_pressure
    target_pressure_curve.setData(target_pressure)

def close_event():
    win.close()
    app.quit()

## MAIN LOOP ##
def main():
    global pressure_data, weight_data, arduino_serial

    # Create packets
    pid_packet = create_pid_packet(500, 3, 0, 4)
    motor_up_packet = create_motor_speed_packet(-100)
    motor_down_packet = create_motor_speed_packet(100)
    stop_packet = create_stop_packet()

    try:
        while True:
            # Connect to Arduino Serial
            try:
                arduino_serial = serial.Serial(port="/dev/cu.usbserial-14610", baudrate=115200, timeout=None)
                if not arduino_serial.is_open:
                    raise Exception("Failed to open serial connection to Arduino")
                print(f"Connected to: {arduino_serial.port}")

                ## AUTO DETECT ONE ARDUINO ##
                # for p in ports:
                #     print(p)

                #     if "Arduino" in p.description:
                #         arduino_port = p.device
                #         break
                
                # if arduino_port:
                #     arduino_serial = serial.Serial(port=arduino_port, baudrate=115200, timeout=None)
                #     if not arduino_serial.is_open:
                #             raise Exception("Failed to open serial connection to Arduino")
                #     print(f"Connected to: {p}")
                # else:
                #     # No Arduino found before loop ends
                #     print(ports)
                #     raise Exception("No Arduino Found. Please check connection")

            except Exception as e:
                print(f"Error: {e}")

            # Wait for Arduino to wake up
            # time.sleep(2)

            arduino_serial.reset_input_buffer()
            arduino_serial.reset_output_buffer()
            
            p = float(input("Enter P value: "))
            i = float(input("Enter I value: "))
            d = float(input("Enter D value: "))
            setpoint = float(input("Enter setpoint value: "))
            targetWeight = float(input("Enter target weight value: "))

            packet = create_pid_packet(p, i, d, setpoint, targetWeight)
            arduino_serial.write(packet)
            start_plotting(p, i, d, setpoint, targetWeight, packet)
            
            arduino_serial.close()
    except KeyboardInterrupt:
        print("Keyboard Interrupted")
        arduino_serial.write(stop_packet)
        arduino_serial.close()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(0)
    finally:
        arduino_serial.write(stop_packet)
        arduino_serial.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
    sys.exit(0)