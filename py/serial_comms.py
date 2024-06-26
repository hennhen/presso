import time
from random import randint
from enum import Enum
import struct

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

sys.path.insert(1, 'py/Symposium UI/')

from serial_communicator import SerialCommunicator
from commands_list import Command

QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self, arduino_serial: SerialCommunicator, p, i, d):
        super().__init__()

        self.p = p
        self.i = i
        self.d = d

        self.arduino_serial = arduino_serial

        self.pressures = []
        self.target_pressures = []
        self.duty_cycles = []
        self.weights = []

        # Create a central widget to hold the plots
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(layout)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # Ensure the window is deleted when closed

        self.title_label = QtWidgets.QLabel()
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setFont(QtGui.QFont('Helvetica', 15))
        self.title_label.setText(f"P = {self.p}\n I = {self.i}\n D = {self.d}")

        layout.addWidget(self.title_label)

        # Add stop button
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_communication)
        layout.addWidget(self.stop_button)

        # Pressures Plot
        self.pressure_plot = pg.PlotWidget()
        layout.addWidget(self.pressure_plot)
        self.setup_pressure_plot()

        # Duty Cycle Plot
        self.duty_cycle_plot = pg.PlotWidget()
        layout.addWidget(self.duty_cycle_plot)
        self.setup_duty_cycle_plot()

        # Weight Plot
        self.weight_plot = pg.PlotWidget()
        layout.addWidget(self.weight_plot)
        self.setup_weight_plot()

        # Add a timer to simulate new temperature measurements
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.receive_serial_data)
        print("Waiting to receive start packet")
        while not self.receive_serial_data():
            pass
        print("Received start packet")
        self.timer.start()

    def stop_communication(self):
        # Stop the timer to halt receiving serial data
        self.timer.stop()
        # Send the stop command to the Arduino
        self.arduino_serial.send_command(Command.STOP)
        # Optionally, reset the UI or do any additional cleanup here

    def setup_pressure_plot(self):
        # self.pressure_plot.setBackground("w")

        pressure_pen = pg.mkPen(color="r", width=1)
        pressure_target_pen = pg.mkPen(color="g", width=1, style=QtCore.Qt.DashLine)

        self.pressure_plot.setTitle("Presureee", color="r", size="20pt")
        axis_name_styles = {"color": "red", "font-size": "18px"}
        self.pressure_plot.setLabel("left", "Pressure (bars)", **axis_name_styles)
        self.pressure_plot.setLabel("bottom", "Time (time)", **axis_name_styles)

        self.pressure_plot.showGrid(x=True, y=True)
        self.pressure_plot.setYRange(0, 12)

        # Get line references for updating the data
        self.pressure_line = self.pressure_plot.plot(self.pressures, name="Pressure", pen=pressure_pen,)
        # self.pressure_line = pg.PlotDataItem(symbol='o', pen=None, symbolSize=1, synbolBrush='r')
        self.pressure_plot.addItem(self.pressure_line)

        self.pressure_target_line = self.pressure_plot.plot(self.target_pressures,name="Target Pressure",pen=pressure_target_pen,)

    def setup_duty_cycle_plot(self):
        # Configure the duty cycle plot
        # self.duty_cycle_plot.setBackground("w")
        duty_cycle_pen = pg.mkPen(color="y", width=1)
        self.duty_cycle_plot.setTitle("Duty Cycle", color="r", size="20pt")
        self.duty_cycle_plot.setLabel("left", "Duty Cycle (%)", **{"color": "red", "font-size": "18px"})
        self.duty_cycle_plot.setLabel("bottom", "Time", **{"color": "red", "font-size": "18px"})
        self.duty_cycle_plot.showGrid(x=True, y=True)
        self.duty_cycle_plot.setYRange(0, 160)

        # GEt line references for updating the data
        self.duty_cycle_line = self.duty_cycle_plot.plot(self.duty_cycles, name="Duty Cycle", pen=duty_cycle_pen)
        # self.duty_cycle_line = pg.PlotDataItem(symbol='o', pen=None, symbolSize=1, symbolBrush='y')
        self.duty_cycle_plot.addItem(self.duty_cycle_line)

    def setup_weight_plot(self):
        # Configure the weight plot
        # self.weight_plot.setBackground("w")
        weight_pen = pg.mkPen(color="m", width=1)
        self.weight_plot.setTitle("Weight", color="r", size="20pt")
        self.weight_plot.setLabel("left", "Weight (g)", **{"color": "red", "font-size": "18px"})
        self.weight_plot.setLabel("bottom", "Time", **{"color": "red", "font-size": "18px"})
        self.weight_plot.showGrid(x=True, y=True)
        self.weight_plot.setYRange(0, 60)

        # Get line references for updating the data
        self.weight_line = self.weight_plot.plot(self.weights, name="Weight", pen=weight_pen)
        # self.weight_line = pg.PlotDataItem(symbol='o', pen=None, symbolSize=1, symbolBrush='m')
        self.weight_plot.addItem(self.weight_line)

    def receive_serial_data(self):
        command, value = self.arduino_serial.receive_response()
        # print("Recieved Command: {0}, Value: {1}".format(command, value))

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
                # print(f"Duty Cycle: {value}")
                self.update_duty_cycle_plot(value)
            elif command == Command.WEIGHT_READING.value:
                # print(f"Weight Reading: {value}")
                self.update_weight_plot(value)
            elif command == Command.EXTRACTION_STARTED.value:
                return True

    def update_pressure_plot(self, pressure):
        self.pressures.append(pressure)
        self.pressure_line.setData(self.pressures)
    
    def update_target_pressure_plot(self, target_pressure):
        self.target_pressures.append(target_pressure)
        self.pressure_target_line.setData(self.target_pressures)
    
    def update_duty_cycle_plot(self, duty_cycle):
        self.duty_cycles.append(duty_cycle)
        self.duty_cycle_line.setData(self.duty_cycles)
    
    def update_weight_plot(self, weight):
        self.weights.append(weight)
        self.weight_line.setData(self.weights)

    def close_event(self):
        print("closed")
        self.close()

# Will be used to create new application window and graphs
# Takes in arduino serial object and PID values
# Sends the PID values to the arduino and starts the graph
class GraphLauncher():
    def __init__(self, arduino_serial, p, i, d):
        arduino_serial.send_command(Command.SET_PID_VALUES, p, i, d, 1, 0)
        self.app = QtWidgets.QApplication([])
        self.main = PlotWindow(arduino_serial, p, i, d)
        self.main.setGeometry(50, 50, 1000, 800)
        self.main.show()
        self.app.aboutToQuit.connect(self.close_event)
        self.app.exec_()

    def close_event(self):
        self.arduino_serial.send_command(Command.STOP)
        print("requested stop")
        self.main.close_event()

if __name__ == "__main__":
    
    # Connect to the Arduino
    arduino_serial = SerialCommunicator(baudrate=250000)
    try:
        arduino_serial.connect_id(target_vid="1A86", target_pid="7523")
        if arduino_serial.serial.is_open:
            print("Connected to {0}.".format(arduino_serial.port))
        else:
            print("Could not connect to Arduino.")
            sys.exit(1)
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
        sys.exit(1)

    # app = QtWidgets.QApplication([])
    # main = PlotWindow(arduino_serial, 1, 1, 1)
    # main.setGeometry(50, 50, 1000, 700)
    # main.show()
    # app.exec()

    # Get the PID values from the user
    p = float(input("Enter P value: "))
    i = float(input("Enter I value: "))
    d = float(input("Enter D value: "))

    # Send the PID values to the Arduino
    # arduino_serial.send_command(Command.SET_PID_VALUES, p, i, d, 1, 0)

    # app = QtWidgets.QApplication([])
    # main = PlotWindow(arduino_serial, p, i, d)
    # main.setGeometry(50, 50, 1000, 800)
    # main.show()
    # app.exec()

    graph_launcher = GraphLauncher(arduino_serial, 1,1,1)

    sys.exit(0)