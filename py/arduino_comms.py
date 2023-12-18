import serial
import serial.tools.list_ports as list_ports
import struct
from enum import Enum
from cobs import cobs
from time import sleep
from arduino_commands import Command

class SerialCommunicator:
    def __init__(self, baudrate, timeout=None):
        """
        Initialize the serial communicator without specifying the port.

        :param baudrate: Communication speed, e.g., 9600, 115200.
        :param timeout: Read timeout in seconds. None for blocking mode.
        """
        self.port = None
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
    
    def connect_id(self, target_vid, target_pid):
        """
        Automatically connect to a device with the given VID and PID.
        
        :param target_vid: The Vendor ID of the device as a string.
        :param target_pid: The Product ID of the device as a string.
        """
        available_ports = list_ports.comports()
        for port in available_ports:
            if port.vid is not None and port.pid is not None:
                vid = hex(port.vid).upper()[2:]
                pid = hex(port.pid).upper()[2:]
                if vid == target_vid and pid == target_pid:
                    print(f"Arduino found on port {port.device}")
                    self.port = port.device
                    self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                    return True

    def connect_port(self, port):
        """
        Connect to a specific serial port.

        :param port: The port to connect to (e.g., "COM3" or "/dev/ttyS0").
        """
        try:
            self.port = port
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"Connected to {self.port} at {self.baudrate} baud.")
        except Exception as e:
            print(f"Error connecting to {self.port}: {e}")
            # Optionally, re-raise the exception or handle it

    def send_command(self, command, *args):
        """
        Send a command with optional arguments to the serial connection.

        :param command: Command type from Command Enum.
        :param args: Additional arguments for the command.
        """
        if command == Command.SET_PID_VALUES:
            packet = self.create_pid_packet(*args)
        elif command == Command.SET_MOTOR_SPEED:
            packet = self.create_motor_speed_packet(*args)
        elif command == Command.STOP:
            packet = self.create_stop_packet()
        elif command == Command.PROFILE_SELECTION:
            packet = self.create_profile_selection_packet(*args)
        # Add other command cases as needed

        if self.serial and self.serial.is_open:
            try:
                packet = cobs.encode(packet) + b'\x00'
                self.serial.write(packet)
                print(f"Sent {command.name} command.")
                print(*args)
            except Exception as e:
                print(f"Error sending command: {e}")
    
    def create_pid_packet(self, p, i, d, setpoint, targetWeight=0):
        packet = struct.pack('<hfffff', Command.SET_PID_VALUES.value, p, i, d, setpoint, targetWeight)
        return packet

    def create_profile_selection_packet(self, profile):
        print(profile)
        type = profile['type']
        if type == 'sine':
            amplitude = profile['amplitude']
            frequency = profile['frequency']
            offset = profile['offset']
            duration = profile['duration']
            packet = struct.pack('<hhfffh', Command.PROFILE_SELECTION.value, 11, amplitude, frequency, offset, duration)
            return packet
        elif type == 'static':
            setpoint = profile['setpoint']
            duration = profile['duration']
            packet = struct.pack('<hhfh', Command.PROFILE_SELECTION.value, 12, setpoint, duration)
            return packet

    def create_motor_speed_packet(self, speed):
        packet = struct.pack('<hf', Command.SET_MOTOR_SPEED.value, speed)
        return packet

    def create_stop_packet(self):
        packet = struct.pack('<h', Command.STOP.value)
        return packet

    def receive_response(self):
        """
        Receive and decode a response from the serial connection.
        """
        if self.serial and self.serial.is_open:
            try:
                incoming_bytes = self.serial.read_until(b'\x00')  # Reading until zero byte
                if len(incoming_bytes) < 2:  # At least 2 bytes (for a short command)
                    print("Packet < 2")
                    return None, None

                data_raw = incoming_bytes[:-1]  # Exclude the trailing zero byte

                try:
                    data_decoded = cobs.decode(data_raw)
                except cobs.DecodeError:
                    print("COBS Decode Error")
                    print(data_raw)
                    return None, None

                if len(data_decoded) >= 2:  # At least 2 bytes for command
                    command = struct.unpack('<h', data_decoded[:2])[0]
                    # Process based on command type
                    if command == Command.EXTRACTION_STOPPED.value:
                        return command, None
                    elif command == Command.PRESSURE_READING.value and len(data_decoded) == 6:
                        pressure_value = struct.unpack('<f', data_decoded[2:])[0]
                        return command, pressure_value
                    elif command == Command.WEIGHT_READING.value and len(data_decoded) == 6:
                        weight_value = struct.unpack('<f', data_decoded[2:])[0]
                        return command, weight_value
                    elif command == Command.TARGET_PRESSURE.value and len(data_decoded) == 6:
                        target_pressure_value = struct.unpack('<f', data_decoded[2:])[0]
                        return command, target_pressure_value
                    elif command == Command.DUTY_CYCLE.value and len(data_decoded) == 6:
                        duty_cycle_value = struct.unpack('<f', data_decoded[2:])[0]
                        return command, duty_cycle_value
                else:
                    print("Packet < 2: ")
                    print(data_decoded)
                    return None, None
            except Exception as e:
                print(f"Error receiving response: {e}")
                return None, None
        else:
            print("Serial connection not open.")
            return None, None

    def close(self):
        """
        Close the serial connection.
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Serial connection closed.")

# Usage Example
# Test with setting motor speed
if __name__ == "__main__":
    serial_comm = SerialCommunicator(115200)
    serial_comm.connect_id("1A86", "7523")
    sleep(4)

    serial_comm.send_command(Command.SET_MOTOR_SPEED, 200)
    sleep(3)
    serial_comm.send_command(Command.SET_MOTOR_SPEED, 0)
    serial_comm.close()