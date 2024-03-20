# extraction_settings.py

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLineEdit, QLabel, QRadioButton, QApplication, QFormLayout
)

class ExtractionSettings(QWidget):
    def __init__(self):
        super().__init__()

        # Main vertical layout
        main_layout = QVBoxLayout()

        # PID Settings Group
        pid_group = QGroupBox("Extraction Settings")
        pid_layout = QFormLayout()
        self.pid_fields = {}
        self.p_line_edit = QLineEdit("100")  # Default value set to 100
        pid_layout.addRow("P: ", self.p_line_edit)
        
        self.i_line_edit = QLineEdit("100")  # Default value set to 100
        pid_layout.addRow("I: ", self.i_line_edit)
        
        self.d_line_edit = QLineEdit("100")  # Default value set to 100
        pid_layout.addRow("D: ", self.d_line_edit)
        
        self.sample_time_line_edit = QLineEdit("100")  # Default value set to 100
        pid_layout.addRow("Sample Time: ", self.sample_time_line_edit)
        
        self.duration_line_edit = QLineEdit("100")  # Default value set to 100
        pid_layout.addRow("Duration: ", self.duration_line_edit)
        
        pid_group.setLayout(pid_layout)
        main_layout.addWidget(pid_group)
        self.setLayout(main_layout)

# Test code to create a simple application window and display the ExtractionSettings widget
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    extraction_settings_widget = ExtractionSettings()
    extraction_settings_widget.show()
    sys.exit(app.exec_())