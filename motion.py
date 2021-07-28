# Laurel Carpenter
# 07/28/2021
# adapted from motion_control_gui.py

from PyQt5.QtChart import QChartView, QChart, QLineSeries, QSplineSeries, QValueAxis
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLCDNumber,
        QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QMessageBox)

from dcps import NewportESP301

class Motion(QDialog):
    def __init__(self,parent=None):
        super(Motion,self).__init__(parent)

        self.open_newport('ASRL/dev/ttyUSB0::INSTR')

        self.qTimer=QTimer()
        self.qTimer.setInterval(1000)
        self.qTimer.start()

        #self.qTimer.timeout.connect(self.check_motor1)
        #self.qTimer.timeout.connect(self.check_motor2)
        #self.qTimer.timeout.connect(self.check_pos1)
        #self.qTimer.timeout.connect(self.check_pos2)

        mainLayout=QGridLayout()
        self.create_control_box()
        mainLayout.addWidget(self.control_box)
        self.setLayout(mainLayout)


    def open_newport(self,path):
        self.newport=NewportESP301(path)
        self.newport.open_inst()




