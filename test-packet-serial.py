import serial
import struct
from cobs import cobs
import time

# Serial port configuration
arduino_port = '/dev/cu.usbmodem14601'  # Replace with your Arduino's serial port
baudrate = 115200
timeout = 3  # Timeout for serial read

# Open the serial port
ser = serial.Serial(arduino_port, baudrate=baudrate, timeout=timeout)
print(f'Opened serial port: {arduino_port}')

# COBS delimiter
zero_byte = b'\x00'

def send_packet(data):
    """Send a packet to the Arduino."""
    # Encode the data with COBS
    encoded_data = cobs.encode(data)
    # Send the encoded data with the delimiter
    ser.write(encoded_data + zero_byte)
    print(f"Sent: {data.hex()}")

def receive_packet():
    """Receive a packet from the Arduino."""
    # Read until the COBS packet ending delimiter is found
    packet = ser.read_until(zero_byte)
    print(packet)
    if packet:
        # Decode the COBS data
        try:
            decoded_packet = cobs.decode(packet[:-1])  # Exclude the delimiter
            print(f"Received: {decoded_packet.hex()}")
            return decoded_packet
        except cobs.DecodeError as e:
            print(f"COBS Decode Error: {e}")

try:
    while True:
        # Example data to send
        data_to_send = b'\x01\x02\x03\x04'  # Replace with your data
        send_packet(data_to_send)
        
        # Receive and print the response
        received_data = receive_packet()
        
        time.sleep(1)  # Delay between sends

except KeyboardInterrupt:
    print("\nExiting...")
    ser.close()

except serial.SerialException as e:
    print(f"Serial Exception: {e}")
    ser.close()
