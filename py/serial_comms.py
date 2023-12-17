import time
from random import randint
from enum import Enum
import struct

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime as dt

import serial
import serial.tools.list_ports
from cobs import cobs

import sys

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from arduino_comms import SerialCommunicator
from arduino_commands import Command

class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self, arduino_serial: SerialCommunicator):
        super().__init__()

        self.arduino_serial = arduino_serial
        self.pressures = []
        self.target_pressures = []
        self.duty_cycles = []

        # Create a central widget to hold the plots
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(layout)

        # Pressures Plot
        self.pressure_plot = pg.PlotWidget()
        layout.addWidget(self.pressure_plot)
        self.setup_pressure_plot()

        # Duty Cycle Plot
        self.duty_cycle_plot = pg.PlotWidget()
        layout.addWidget(self.duty_cycle_plot)
        self.setup_duty_cycle_plot()

        # Add a timer to simulate new temperature measurements
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.receive_serial_data)
        self.timer.start()

    def setup_pressure_plot(self):
        self.pressure_plot.setBackground("w")

        pressure_pen = pg.mkPen(color="r", width=2)
        pressure_target_pen = pg.mkPen(color="g", width=2, style=QtCore.Qt.DashLine)

        self.pressure_plot.setTitle("Presureee", color="b", size="20pt")
        axis_name_styles = {"color": "red", "font-size": "18px"}
        self.pressure_plot.setLabel("left", "Pressure (bars)", **axis_name_styles)
        self.pressure_plot.setLabel("bottom", "Time (time)", **axis_name_styles)
        self.pressure_plot.addLegend()

        self.pressure_plot.showGrid(x=True, y=True)
        self.pressure_plot.setYRange(0, 12)

        # Get line references for updating the data
        self.pressure_line = self.pressure_plot.plot(self.pressures, name="Pressure", pen=pressure_pen,)
        self.pressure_target_line = self.pressure_plot.plot(self.target_pressures,name="Target Pressure",pen=pressure_target_pen,)

    def setup_duty_cycle_plot(self):
        # Configure the duty cycle plot
        self.duty_cycle_plot.setBackground("w")
        duty_cycle_pen = pg.mkPen(color="b", width=2)
        self.duty_cycle_plot.setTitle("Duty Cycle", color="b", size="20pt")
        self.duty_cycle_plot.setLabel("left", "Duty Cycle (%)", **{"color": "blue", "font-size": "18px"})
        self.duty_cycle_plot.setLabel("bottom", "Time", **{"color": "blue", "font-size": "18px"})
        self.duty_cycle_plot.showGrid(x=True, y=True)
        self.duty_cycle_plot.setYRange(0, 300)

        # GEt line references for updating the data
        self.duty_cycle_line = self.duty_cycle_plot.plot(self.duty_cycles, name="Duty Cycle", pen=duty_cycle_pen)

    def receive_serial_data(self):
        command, value = self.arduino_serial.receive_response()
        print("Recieved Command: {0}, Value: {1}".format(command, value))

        if command is not None:
            if command == Command.EXTRACTION_STOPPED.value:
                print("Extraction Stopped.")
                self.timer.stop()
            elif command == Command.PRESSURE_READING.value:
                # print(f"Pressure Reading: {value}")
                self.update_pressure_plot(value)  # Update the plot
            elif command == Command.TARGET_PRESSURE.value:
                # print(f"Target Pressure: {value}")
                self.update_target_pressure_plot(value)  # Update the plot
            elif command == Command.DUTY_CYCLE.value:
                print(f"Duty Cycle: {value}")
                self.update_duty_cycle_plot(value)
            elif command == Command.WEIGHT_READING.value:
                print(f"Weight Reading: {value}")
                # weight_data.append(value)
                # update_weight_plot()

    def update_pressure_plot(self, pressure):
        self.pressures.append(pressure)
        self.pressure_line.setData(self.pressures)
    
    def update_target_pressure_plot(self, target_pressure):
        self.target_pressures.append(target_pressure)
        self.pressure_target_line.setData(self.target_pressures)
    
    def update_duty_cycle_plot(self, duty_cycle):
        self.duty_cycles.append(duty_cycle)
        self.duty_cycle_line.setData(self.duty_cycles)

    def close_event(self):
        self.close()

if __name__ == "__main__":
    # Connect to the Arduino
    arduino_serial = SerialCommunicator(baudrate=115200)
    arduino_serial.connect_id(target_vid="1A86", target_pid="7523")
    print("Connected to Arduino")

    # Get the PID values from the user
    p = float(input("Enter P value: "))
    i = float(input("Enter I value: "))
    d = float(input("Enter D value: "))
    setpoint = float(input("Enter setpoint value: "))
    target_weight = float(input("Enter target weight value: "))

    # Send the PID values to the Arduino
    arduino_serial.send_command(Command.SET_PID_VALUES, p, i, d, setpoint, target_weight)

    app = QtWidgets.QApplication([])
    main = PlotWindow(arduino_serial)
    main.show()
    app.exec()
    sys.exit(0)