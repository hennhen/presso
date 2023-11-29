import serial
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
arduino_port = None
s = None

try:
    for p in ports:
        print(p)

        if "Arduino" in p.description:
            arduino_port = p.device
            break
    
    if arduino_port:
        s = serial.Serial(arduino_port, baudrate=9600)
        if not s.is_open:
                raise Exception("Failed to open serial connection to Arduino")
        print(f"Connected to: {p}")
    else:
        # No Arduino found before loop ends
        print(ports)
        raise Exception("No Arduion Found. Please check connection")

except Exception as e:
     print(f"Error: {e}")