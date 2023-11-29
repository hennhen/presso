import serial
import sys
import json
from simple_pid import PID
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time

sys.path.append('/Users/henrywu/Desktop/capstone/roboclaw/lib/python3.7/site-packages/roboclaw_python')
from roboclaw_3 import Roboclaw

# Initialize PID controller settings
P, I, D = 20, 5, 5
setpoint = 8

# Setup serial connection and PID controller
s = serial.Serial(port='/dev/tty.usbmodem1401', baudrate=9600)
pid = PID(P, I, D, setpoint=setpoint)
pid.output_limits = (1, 126)

# Initialize Roboclaw
roboclaw = Roboclaw('/dev/tty.usbmodem2101', 38400)
roboclaw.Open()
MOTOR_ADDRESS = 0x80

# Function to read pressure
def read_pressure():
    buffer = ''
    while True:
        try:
            byte = s.read(1).decode('utf-8', errors='ignore')
            if byte == '<':
                buffer = ''
            elif byte == '>':
                try:
                    data = json.loads(buffer)
                    return data.get('pressure')
                except json.JSONDecodeError:
                    buffer = ''
                    continue
            else:
                buffer += byte
        except UnicodeDecodeError:
            continue

# Plotting setup
fig, ax = plt.subplots()
plt.title(f'Pressure Control: PID({P}, {I}, {D}), Setpoint: {setpoint}')
x_len = 1000  # Length of data to display
pressure_data = deque([0]*x_len, maxlen=x_len)
times = deque([0]*x_len, maxlen=x_len)  # Time tracking
start_time = time.time()  # Start time for the plot

# Pressure plot
line, = ax.plot(times, pressure_data, label="Pressure", color='b')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Pressure (units)', color='b')
ax.tick_params(axis='y', labelcolor='b')
ax.set_ylim(0, 12)
ax.axhline(y=setpoint, color='g', linestyle='--', label='Setpoint')
ax.legend()

# Update plot function
def update_plot(frame):
    current_time = time.time() - start_time
    pressure = read_pressure()
    if pressure is not None:
        motor_speed = pid(pressure)
        pressure_data.append(pressure)
        times.append(current_time)
        line.set_data(times, pressure_data)
        ax.relim()  # Recalculate limits
        ax.autoscale_view()  # Autoscale view

        if motor_speed > 0:
            roboclaw.BackwardM1(MOTOR_ADDRESS, int(motor_speed))
        else:
            roboclaw.ForwardM1(MOTOR_ADDRESS, int(-motor_speed))

    return line,

# Animation
ani = animation.FuncAnimation(fig, update_plot, interval=1)  # Update interval in milliseconds

plt.show()

# Cleanup when the plot is closed
roboclaw.ForwardM1(MOTOR_ADDRESS, 0)
s.close()
