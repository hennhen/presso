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
        elif command == Command.WEIGHT_READING.value and len(data_decoded) == 6:  # New condition for weight command
            weight_value = struct.unpack('<f', data_decoded[2:])[0]
            return command, weight_value
    
    return None, None

## PLOTTING STUFF ##
# Global lists to store time and pressure data
pressure_data = []
weight_data = []

def init_plot(p, i, d, setpoint, target_weight):
    global line, ax, fig, background, pressure_data, weight_data, line2, ax2, background2
    pressure_data.clear()  # Clear the pressure data list
    weight_data.clear()  # Clear the weight data list
    plt.ion()
    fig, (ax, ax2) = plt.subplots(2, 1, constrained_layout=True)  # Create two subplots
    line, = ax.plot([], [], lw=2)  # Initialize an empty line for pressure plot
    line2, = ax2.plot([], [], lw=2)  # Initialize an empty line for weight plot
    ax.axhline(y=setpoint, color='r', linestyle='--')  # Add a horizontal line at the setpoint for pressure plot
    ax2.axhline(y=target_weight, color='g', linestyle='--')  # Add a horizontal line at the target weight for weight plot
    ax.set_title(f"Pressure for Setpoint: {setpoint}, P: {p}, I:{i}, D:{d}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Pressure")
    ax.set_ylim(0, 10)
    ax2.set_title("Weight")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Weight")
    ax2.set_ylim(0, 15)
    fig.canvas.draw()  # Draw the figure canvas
    background = fig.canvas.copy_from_bbox(ax.bbox)  # Save the state of the background for pressure plot
    background2 = fig.canvas.copy_from_bbox(ax2.bbox)  # Save the state of the background for weight plot

def update_pressure_plot(pressure_data):
    if pressure_data:
        line.set_data(range(len(pressure_data)), pressure_data)  # Update the line data
        ax.relim()
        ax.autoscale_view(True, True, True)
        fig.canvas.restore_region(background)  # Restore the background
        ax.draw_artist(line)  # Draw the line
        fig.canvas.blit(ax.bbox)  # Blit the axes bounding box
        fig.canvas.flush_events()

def update_weight_plot(weight_data):
    if weight_data:
        line2.set_data(range(len(weight_data)), weight_data)  # Update the line data
        ax2.relim()
        ax2.autoscale_view(True, True, True)
        fig.canvas.restore_region(background2)  # Restore the background
        ax2.draw_artist(line2)  # Draw the line
        fig.canvas.blit(ax2.bbox)  # Blit the axes bounding box
        fig.canvas.flush_events()

## MAIN LOOP ##
def main():
    global pressure_data

    # Create packets
    pid_packet = create_pid_packet(500, 3, 0, 4)
    motor_up_packet = create_motor_speed_packet(-100)
    motor_down_packet = create_motor_speed_packet(100)
    stop_packet = create_stop_packet()

    try:
        while True:
            # Connect to Arduino Serial
            try:
                # arduino_serial = serial.Serial(port="/dev/cu.usbmodem144101", baudrate=115200, timeout=None)
                # if not arduino_serial.is_open:
                #     raise Exception("Failed to open serial connection to Arduino")
                # print(f"Connected to: {arduino_serial.port}")

                ## AUTO DETECT ONE ARDUINO ##
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

            # Wait for Arduino to wake up
            time.sleep(2)

            arduino_serial.reset_input_buffer()
            arduino_serial.reset_output_buffer()
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
                targetWeight = float(input("Enter target weight value: "))
                init_plot(p, i, d, setpoint, targetWeight)

                packet = create_pid_packet(p, i, d, setpoint, targetWeight)
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
                            update_pressure_plot(pressure_data)  # Update the plot
                        elif command == Command.WEIGHT_READING.value:
                            print(f"Weight Reading: {value}")
                            weight_data.append(value)
                            update_weight_plot(weight_data)

            elif text == 'stop':
                arduino_serial.write(stop_packet)

            elif text == 'exit':
                break

            else:
                print("Invalid command.")

            arduino_serial.close()
    except KeyboardInterrupt:
        print("Keyboard Interrupted")
        arduino_serial.write(stop_packet)
        arduino_serial.close()
        sys.exit(0)
            
    finally:
        arduino_serial.write(stop_packet)
        arduino_serial.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
    sys.exit(0)