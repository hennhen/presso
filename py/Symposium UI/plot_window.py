import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore, QtGui
from commands_list import Command
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QApplication

QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self, arduino_serial):
        super().__init__()

        self.arduino_serial = arduino_serial

        self.pressures = []
        self.target_pressures = []
        self.duty_cycles = []
        self.weights = []

        self.init_ui()
        self.setup_plots()

    def init_ui(self):
        # Create a central widget to hold the plots
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(layout)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # Ensure the window is deleted when closed

        # Title label
        # self.title_label = QtWidgets.QLabel(f"P = {self.p}, I = {self.i}, D = {self.d}", alignment=QtCore.Qt.AlignCenter)
        # layout.addWidget(self.title_label)

        # Stop button
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_communication)
        layout.addWidget(self.stop_button)

    def setup_plots(self):
        # Pressure Plot
        self.pressure_plot = pg.PlotWidget(name='Pressure')
        self.pressure_plot.setTitle("Pressure")
        self.pressure_plot.setLabel('left', 'Pressure', units='Pa')
        self.pressure_plot.setLabel('bottom', 'Time', units='s')
        self.pressure_line = self.pressure_plot.plot(self.pressures, pen='r')
        self.centralWidget().layout().addWidget(self.pressure_plot)

        # Duty Cycle Plot
        self.duty_cycle_plot = pg.PlotWidget(name='Duty Cycle')
        self.duty_cycle_plot.setTitle("Duty Cycle")
        self.duty_cycle_plot.setLabel('left', 'Duty Cycle', units='%')
        self.duty_cycle_plot.setLabel('bottom', 'Time', units='s')
        self.duty_cycle_line = self.duty_cycle_plot.plot(self.duty_cycles, pen='y')
        self.centralWidget().layout().addWidget(self.duty_cycle_plot)

        # Weight Plot
        self.weight_plot = pg.PlotWidget(name='Weight')
        self.weight_plot.setTitle("Weight")
        self.weight_plot.setLabel('left', 'Weight', units='g')
        self.weight_plot.setLabel('bottom', 'Time', units='s')
        self.weight_line = self.weight_plot.plot(self.weights, pen='b')
        self.centralWidget().layout().addWidget(self.weight_plot)

    @pyqtSlot(object, object)
    def update_plots(self, command, value):
        # This slot will be called whenever new data is received
        if command == Command.PRESSURE_READING.value:
            self.update_pressure_plot(value)
        elif command == Command.DUTY_CYCLE.value:
            self.update_duty_cycle_plot(value)
        elif command == Command.WEIGHT_READING.value:
            self.update_weight_plot(value)
        # Add other conditions for different types of data as needed


    def receive_serial_data(self):
        # This method should be connected to the signal from the SerialWorker
        # For now, it's just a placeholder
        pass

    def update_pressure_plot(self, pressure):
        self.pressures.append(pressure)
        self.pressure_line.setData(self.pressures)

    def update_duty_cycle_plot(self, duty_cycle):
        self.duty_cycles.append(duty_cycle)
        self.duty_cycle_line.setData(self.duty_cycles)

    def update_weight_plot(self, weight):
        self.weights.append(weight)
        self.weight_line.setData(self.weights)

    def stop_communication(self):
        self.timer.stop()
        self.arduino_serial.send_command(Command.STOP)

    def closeEvent(self, event):
        self.stop_communication()
        event.accept()

