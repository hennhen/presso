import serial
import json

# Setup serial connection
s = serial.Serial(port='/dev/tty.usbmodem1401', baudrate=9600)

def read_pressure():
    buffer = ''
    while True:
        try:
            # Read one byte at a time
            byte = s.read(1).decode('utf-8', errors='ignore')  # Ignore invalid UTF-8 characters

            if byte == '<':  # Start of new message
                buffer = ''
            elif byte == '>':  # End of message
                try:
                    # Parse the JSON data
                    data = json.loads(buffer)
                    return data.get('pressure')
                except json.JSONDecodeError:
                    # Reset the buffer on decode error
                    buffer = ''
                    print("JSON decode error. Resetting buffer.")
                    continue
            else:
                buffer += byte
        except UnicodeDecodeError:
            # Handle invalid byte sequences
            print("Unicode decode error. Skipping byte.")

while True:
    print(read_pressure())
