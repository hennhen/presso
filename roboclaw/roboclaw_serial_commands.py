import serial

def crc16(data: bytes, offset, length):
    crc = 0
    for i in range(offset, length + offset):
        crc ^= data[i] << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF
    return crc

def connect_roboclaw(com_port, baud_rate):
    return serial.Serial(com_port, baudrate=baud_rate, timeout=1)

def write_roboclaw(serial_connection, address, command, values=[]):
    data = bytes([address]) + bytes([command]) + bytes(values)
    crc = crc16(data, 0, len(data))
    data += bytes([crc >> 8, crc & 0xFF])
    serial_connection.write(data)

def read_roboclaw(serial_connection, num_bytes):
    return serial_connection.read(num_bytes)

def read_standard_config(serial_connection, address):
    write_roboclaw(serial_connection, address, 99)
    response = read_roboclaw(serial_connection, 4)  # Expecting 4 bytes back: 2 bytes config, 2 bytes CRC
    if len(response) == 4:
        # Combine address, command, and data bytes to calculate CRC
        crc_check_data = bytes([address, 99]) + response[0:2]
        crc_received = response[2:4]
        crc_calculated = crc16(crc_check_data, 0, len(crc_check_data))

        crc_received_val = int.from_bytes(crc_received, byteorder='big')
        if crc_received_val == crc_calculated:
            config = int.from_bytes(response[0:2], byteorder='big')
            return config
        else:
            raise ValueError("CRC mismatch")
    else:
        raise ValueError("Invalid response length")
    
def read_battery_voltage_offsets(serial_connection, address):
    write_roboclaw(serial_connection, address, 116)
    # We expect 4 bytes back: 1 byte MainBatteryOffset, 1 byte LogicBatteryOffset, 2 bytes CRC
    response = read_roboclaw(serial_connection, 4)
    if len(response) == 4:
        # Calculate CRC
        crc_check_data = bytes([address, 116]) + response[0:2]
        crc_received = response[2:4]
        crc_calculated = crc16(crc_check_data, 0, len(crc_check_data))
        
        crc_received_val = int.from_bytes(crc_received, byteorder='big')
        if crc_received_val == crc_calculated:
            # Correct conversion from byte values back to voltage offsets
            main_battery_offset = (response[0] / 20) - 10
            logic_battery_offset = (response[1] / 20) - 10
            return main_battery_offset, logic_battery_offset
        else:
            raise ValueError("CRC mismatch")
    else:
        raise ValueError("Invalid response length")

    
def set_battery_voltage_offsets(serial_connection, address, main_offset, logic_offset):
    """
    Set the main and logic battery voltage offsets.

    :param serial_connection: The serial connection to the RoboClaw
    :param address: The address byte of the RoboClaw
    :param main_offset: The offset for the main battery voltage in volts
    :param logic_offset: The offset for the logic battery voltage in volts
    :return: True if successful, False otherwise
    """
    try:
        # Convert voltage offsets to byte values within the range of -10 to 10
        main_offset_byte = int((main_offset + 10) * 10)  # Converts to 0-200
        logic_offset_byte = int((logic_offset + 10) * 10)  # Converts to 0-200

        # Ensure the byte values are within 0-255
        if not (0 <= main_offset_byte <= 255 and 0 <= logic_offset_byte <= 255):
            raise ValueError("Offset values must be in the range of -10 to 10.")

        # Construct the command packet
        command = [address, 115, main_offset_byte, logic_offset_byte]

        # Calculate CRC16
        crc = crc16(command, 0, len(command))
        command += [crc >> 8, crc & 0xFF]

        # Send command to RoboClaw
        serial_connection.write(bytearray(command))

        # Read the response from RoboClaw
        response = serial_connection.read(1)
        if response and ord(response) == 0xFF:
            return True
        return False
    except (ValueError, serial.SerialException) as e:
        print(f"Error setting battery voltage offsets: {e}")
        return False


def main():
    roboclaw_port = '/dev/tty.usbmodem111101'  # Replace with the correct port
    roboclaw_baud = 38400         # Use the appropriate baud rate
    roboclaw_address = 0x80       # Replace with the correct address

    roboclaw = connect_roboclaw(roboclaw_port, roboclaw_baud)

    desired_main_battery_offset = 10  # Replace with desired offset value
    desired_logic_battery_offset = 10 # Replace with desired offset value

    try:
        # Set new battery voltage offsets
        success = set_battery_voltage_offsets(roboclaw, roboclaw_address, desired_main_battery_offset, desired_logic_battery_offset)
        if success:
            print("Successfully updated battery voltage offsets.")
        else:
            print("Failed to update battery voltage offsets.")

        # Read back the battery voltage offsets to confirm
        main_battery_offset, logic_battery_offset = read_battery_voltage_offsets(roboclaw, roboclaw_address)
        print(f"Read Main Battery Offset: {main_battery_offset}")
        print(f"Read Logic Battery Offset: {logic_battery_offset}")

    except ValueError as e:
        print(e)
    finally:
        roboclaw.close()

if __name__ == "__main__":
    main()