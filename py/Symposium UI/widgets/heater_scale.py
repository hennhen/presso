from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QApplication, QGroupBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class HeaterScale(QWidget):
    def __init__(self):
        super().__init__()

        # Main horizontal layout
        hbox_layout = QHBoxLayout()

        # Group for the scale
        scale_group = QGroupBox("Weight")
        scale_layout = QVBoxLayout()
        weight_label = QLabel("26.7g")
        weight_label.setFont(QFont(None, 24, QFont.Bold))
        weight_label.setAlignment(Qt.AlignCenter)
        scale_layout.addWidget(weight_label)
        # scale_layout.addItem(QSpacerItem(1, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Spacer
        tare_button = QPushButton("Tare")
        scale_layout.addWidget(tare_button, alignment=Qt.AlignCenter)
        scale_group.setLayout(scale_layout)

        # Group for the heater
        heater_group = QGroupBox("Temperature")
        heater_layout = QVBoxLayout()
        current_temp_label = QLabel("78°C")
        current_temp_label.setFont(QFont(None, 24, QFont.Bold))
        current_temp_label.setAlignment(Qt.AlignCenter)
        heater_layout.addWidget(current_temp_label)

        # Smaller label for the target temperature
        target_temp_display_label = QLabel("93°C")
        target_temp_display_label.setFont(QFont(None, 12))  # Smaller font size than the current temperature
        target_temp_display_label.setAlignment(Qt.AlignCenter)
        heater_layout.addWidget(target_temp_display_label)

        # heater_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Spacer

        # Vertical layout for the target temperature input and button
        target_temp_layout = QVBoxLayout()
        set_temp_label = QLineEdit()
        set_temp_label.setAlignment(Qt.AlignCenter)
        set_temp_button = QPushButton("Set")

        target_temp_layout.addWidget(set_temp_label)
        target_temp_layout.addWidget(set_temp_button)
        heater_layout.addLayout(target_temp_layout)

        heater_group.setLayout(heater_layout)

        # Add the groups to the horizontal layout
        hbox_layout.addWidget(scale_group)
        hbox_layout.addWidget(heater_group)

        # Set the main layout for the widget
        self.setLayout(hbox_layout)

# Test code to create a simple application window and display the HeaterScale widget
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    heater_scale_widget = HeaterScale()
    heater_scale_widget.show()
    sys.exit(app.exec_())