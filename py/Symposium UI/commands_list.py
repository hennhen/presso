from enum import Enum

class Command(Enum):
    """ Enum for command types """
    SET_MOTOR_SPEED = 1
    SET_PID_VALUES = 2
    SET_PRESSURE = 3
    STOP = 4
    HEATER_SETPOINT = 13
    TARE = 14
    START_PARTIAL_EXTRACTION = 15
    START_FULL_EXTRACTION = 16

    # Responses
    DUTY_CYCLE = 5
    TARGET_PRESSURE = 6
    WEIGHT_READING = 7
    EXTRACTION_STOPPED = 8
    PRESSURE_READING = 9
    PROFILE_SELECTION = 10
    EXTRACTION_STARTED = 17
    TEMPERATURE = 18

# Add any related functions or classes here if needed
