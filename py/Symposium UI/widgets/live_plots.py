import sys
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore, QtGui
from commands_list import Command
from PyQt5.QtCore import pyqtSlot, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication

QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

class LivePlotWidget(QtWidgets.QWidget):
    extraction_plot_signal = pyqtSignal(object)
    def __init__(self, arduino_serial):
        super().__init__()

        self.arduino_serial = arduino_serial

        self.pressures = []
        self.target_pressures = []
        self.duty_cycles = []
        self.weights = []
        self.currents = []

        self.init_ui()
        self.setup_plots()

    def init_ui(self):
        # Create a central widget to hold the plots

        self.layout = QtWidgets.QVBoxLayout(self)

        # Title label
        self.title_label = QtWidgets.QLabel(f"Live Plots", alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title_label)


    def setup_plots(self):
        # Pressure Plot
        self.pressure_plot = pg.PlotWidget(name='Pressure')
        self.pressure_plot.setTitle("Pressure")
        self.pressure_plot.setLabel('left', 'Pressure', units='Bar')
        self.pressure_plot.setLabel('bottom', 'Time', units='s')
        self.pressure_plot.setYRange(0, 12)
        self.pressure_line = self.pressure_plot.plot(self.pressures, pen='r')
        self.pressure_target_line = self.pressure_plot.plot(self.target_pressures,name="Target Pressure")
        self.layout.addWidget(self.pressure_plot)

        # Duty Cycle Plot
        self.duty_cycle_plot = pg.PlotWidget(name='Duty Cycle')
        self.duty_cycle_plot.setTitle("Duty Cycle")
        self.duty_cycle_plot.setLabel('left', 'Duty Cycle', units='%')
        self.duty_cycle_plot.setLabel('bottom', 'Time', units='s')
        self.duty_cycle_line = self.duty_cycle_plot.plot(self.duty_cycles, pen='y')
        self.layout.addWidget(self.duty_cycle_plot)

        # Weight Plot
        self.weight_plot = pg.PlotWidget(name='Weight')
        self.weight_plot.setTitle("Weight")
        self.weight_plot.setLabel('left', 'Weight', units='g')
        self.weight_plot.setLabel('bottom', 'Time', units='s')
        self.weight_line = self.weight_plot.plot(self.weights, pen='b')
        self.layout.addWidget(self.weight_plot)

        # Motor Current Plot
        self.motor_current_plot = pg.PlotWidget(name='Motor Current')
        self.motor_current_plot.setTitle("Motor Current")
        self.motor_current_plot.setLabel('left', 'Current', units='A')
        self.motor_current_plot.setLabel('bottom', 'Time', units='s')
        self.motor_current_line = self.motor_current_plot.plot(self.currents, pen='g')
        self.layout.addWidget(self.motor_current_plot)

    @pyqtSlot(object, object)
    def update_plots(self, command, value):
        # This slot will be called whenever new data is received
        if command == Command.PRESSURE_READING.value:
            self.update_pressure_plot(value)
        elif command == Command.DUTY_CYCLE.value:
            self.update_duty_cycle_plot(value)
        elif command == Command.WEIGHT_READING.value:
            self.update_weight_plot(value)
        elif command == Command.EXTRACTION_STOPPED.value:
            self.extraction_plot_signal.emit(1)
        elif command == Command.TARGET_PRESSURE.value:
            self.update_target_pressure_plot(value)
        elif command == Command.MOTOR_CURRENT.value:
            self.update_motor_current_plot(value)
        # Add other conditions for different types of data as needed

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
    
    def update_motor_current_plot(self, motor_current):
        self.currents.append(motor_current)
        self.motor_current_line.setData(self.currents)

    def clear_plots(self):
        self.pressures.clear()
        self.pressure_line.clear()

        self.target_pressures.clear()
        self.pressure_target_line.clear()
        
        self.duty_cycles.clear()
        self.duty_cycle_line.clear()

        self.weights.clear()
        self.weight_line.clear()    
        
        self.currents.clear()
        self.motor_current_line.clear()

class MainTestWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Main Control Panel with Embedded Plot')

        # Create an instance of PlotWidget
        self.plot_widget = LivePlotWidget(self)

        # Set the central widget of the main window to be the PlotWidget
        self.setCentralWidget(self.plot_widget)

        # You can set up additional UI elements here as needed

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainTestWindow()
    main_window.show()
    sys.exit(app.exec_())

