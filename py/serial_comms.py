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

    EXTRACTION_STOPPED = 8
    PRESSURE_READING = 9

# Connect to Arduino Serial
try:
    arduino_serial = serial.Serial(port="/dev/cu.usbmodem144101", baudrate=115200, timeout=None)
    if not arduino_serial.is_open:
        raise Exception("Failed to open serial connection to Arduino")
    print(f"Connected to: {arduino_serial.port}")

    # for p in ports:
    #     # print(p)

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

""" Command Packet Creators """
def create_pid_packet(p, i, d, setpoint):
    # SUPER IMPORTANT
    packet = struct.pack('<hffff', Command.SET_PID_VALUES.value, p, i, d, setpoint)
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
    incoming_bytes = serial_conn.read_until(zeroByte)
    if len(incoming_bytes) < 2:  # At least 2 bytes (for a short command)
        print("Packet < 2")
        return None, None

    data_raw = incoming_bytes[:-1]  # Exclude the trailing zero byte
    data_decoded = cobs.decode(data_raw)
    
    if len(data_decoded) >= 2:  # At least 2 bytes for command
        command = struct.unpack('<h', data_decoded[:2])[0]

        if command == Command.EXTRACTION_STOPPED.value:
            return command, None
        elif command == Command.PRESSURE_READING.value and len(data_decoded) == 6:  # command + float
            pressure_value = struct.unpack('<f', data_decoded[2:])[0]
            return command, pressure_value
    
    return None, None

## PLOTTING STUFF ##
# Global lists to store time and pressure data
pressure_data = []

def init_plot(p, i, d, setpoint):
    global line, ax, fig, background, pressure_data
    pressure_data.clear()  # Clear the data list
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)  # Initialize an empty line
    ax.axhline(y=setpoint, color='r', linestyle='--')  # Add a horizontal line at the setpoint
    ax.set_title(f"Pressure for Setpoint: {setpoint}, P: {p}, I:{i}, D:{d}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Pressure")
    ax.set_ylim([0, 10])  # Set y-axis limits
    fig.canvas.draw()  # Draw the figure canvas
    background = fig.canvas.copy_from_bbox(ax.bbox)  # Save the state of the background
    
def update_plot(pressure_data):
    if pressure_data:
        line.set_data(range(len(pressure_data)), pressure_data)  # Update the line data
        ax.relim()
        ax.autoscale_view(True, True, True)
        fig.canvas.restore_region(background)  # Restore the background
        ax.draw_artist(line)  # Draw the line
        fig.canvas.blit(ax.bbox)  # Blit the axes bounding box
        fig.canvas.flush_events()

## MAIN LOOP ##
def main():
    global pressure_data

    # Wait for Arduino to wake up
    time.sleep(2)

    arduino_serial.reset_input_buffer()
    arduino_serial.reset_output_buffer()

    # Create packets
    pid_packet = create_pid_packet(500, 3, 0, 4)
    motor_up_packet = create_motor_speed_packet(-100)
    motor_down_packet = create_motor_speed_packet(100)
    stop_packet = create_stop_packet()

    try:
        while True:
            # Get user input
            text = input("Enter command (up/down/pid/stop/exit): ").strip().lower()

            # Handle the user input
            if text == 'up':
                arduino_serial.write(motor_up_packet)
                time.sleep(1)
                arduino_serial.write(stop_packet)

            elif text == 'down':
                arduino_serial.write(motor_down_packet)
                time.sleep(1)
                arduino_serial.write(stop_packet)

            elif text == 'pid':
                p = float(input("Enter P value: "))
                i = float(input("Enter I value: "))
                d = float(input("Enter D value: "))
                setpoint = float(input("Enter setpoint value: "))
                init_plot(p, i, d, setpoint)

                packet = create_pid_packet(p, i, d, setpoint)
                arduino_serial.write(packet)

                # Read Pressure
                while True:
                    command, value = receive_command(arduino_serial)
                    print("Recieved Command: {0}, Value: {1}".format(command, value))

                    if command is not None:
                        if command == Command.EXTRACTION_STOPPED.value:
                            print("Extraction Stopped.")
                            break
                        elif command == Command.PRESSURE_READING.value:
                            print(f"Pressure Reading: {value}")
                            pressure_data.append(value)  # Append only the pressure value
                            update_plot(pressure_data)  # Update the plot

            elif text == 'stop':
                arduino_serial.write(stop_packet)

            elif text == 'exit':
                break

            else:
                print("Invalid command.")   
    except KeyboardInterrupt:
        print("Keyboard Interrupted")
        arduino_serial.write(stop_packet)
        sys.exit(0)
    finally:
        print("Finally")
        arduino_serial.write(stop_packet)
        sys.exit(0)


if __name__ == "__main__":
    main()
    sys.exit(0)

try:
    # Sending PID packet
    arduino_serial.write(pid_packet)

    # # Sending Motor Speed packet
    # arduino_serial.write(motor_speed_packet)
    # time.sleep(2)

    # Loop to read Arduino pressure feedback
    while(True):
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

    # Sending Stop packet
    num_of_outgoing_bytes = arduino_serial.write(stop_packet)
    print( "python wrote {0} bytes. command_encoded: {1}".format(num_of_outgoing_bytes, stop_packet))
    time.sleep(2)

except Exception as e:
    print(f"Error: {e}")
finally:
    arduino_serial.close()
    sys.exit()  # Exit the program


while True:
    pass


## ARCHIVE ##

buffer = bytearray()

SET_MOTOR_SPEED = 0x04

command = struct.pack("<hf", 4, 4.7321)
print(len(command))
command_encoded = cobs.encode(command) 
print(len(command_encoded))



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