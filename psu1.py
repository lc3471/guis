# Laurel Carpenter
# 07/28/2021
# adapted from psu_gui.py

from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLCDNumber,
        QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QMessageBox)

from dcps import AimTTiEL302P
from pyvisa.errors import VisaIOError
from serial.serialutil import SerialException

class PSU1(QDialog):
    def __init__(self,parent=None):
        super(PSU1,self).__init__(parent)

        mainLayout = QGridLayout()
        
        try:
            self.createPSU1Box()
            self.isConnected=True
        except VisaIOError as err:
            self.PSU1Box=QLabel("PSU 1 Not Connected: "+str(err))
            self.isConnected=False
        except SerialException as err:
            self.PSU1Box=QLabel("PSU 1 Not Connected: "+str(err))
            self.isConnected=False

        self.setLayout(mainLayout)
        mainLayout.addWidget(self.PSU1Box,0,0)

    def createPSU1Box(self):
        self.aim1 = AimTTiEL302P('ASRL/dev/ttyACM1::INSTR')
        self.aim1.open()

        # create the displays for the measurements of I and V
        self.VmeasNumber = QLCDNumber()
        self.VmeasNumber.setSegmentStyle(QLCDNumber.Flat)
        self.Vmeas = self.aim1.measureVoltage()

        self.ImeasNumber = QLCDNumber()
        self.ImeasNumber.setSegmentStyle(QLCDNumber.Flat)
        self.Imeas = self.aim1.measureCurrent()

        self.was_on_PSU1=self.aim1.isOutputOn()

        self.qTimer = QTimer()
        self.qTimer.setInterval(500)
        self.qTimer.start()

        self.qTimer.timeout.connect(self.query_voltage_PSU1)
        self.qTimer.timeout.connect(self.query_current_PSU1)
        self.qTimer.timeout.connect(self.measure_voltage_PSU1)
        self.qTimer.timeout.connect(self.measure_current_PSU1)
        self.qTimer.timeout.connect(self.check_output_PSU1)

        ##Creates a PSU Box, calls functions to create the Vbox and Ibox that go inside.
        self.PSU1Box = QGroupBox("Single PSU")
        self.PSU1Box.setObjectName("psu1")
        #self.PSU1Box.setStyleSheet("QGroupBox#psu1 { font-weight: bold; }")

        self.PSU1Layout = QGridLayout()
        self.PSU1Box.setLayout(self.PSU1Layout)

        self.create_Vbox_PSU1()
        self.create_Ibox_PSU1()
        self.PSU1Layout.addWidget(self.Vbox_PSU1,0,0)
        self.PSU1Layout.addWidget(self.Ibox_PSU1,0,1)

        self.create_Obox_PSU1()
        self.PSU1Layout.addWidget(self.Obox_PSU1,0,2)

    def create_Vbox_PSU1(self):
        self.Vbox_PSU1 = QGroupBox("Voltage")
        self.Vlayout_PSU1 = QVBoxLayout()
        self.Vbox_PSU1.setLayout(self.Vlayout_PSU1)

        self.PSU1vPrompt = QLabel("Voltage [V]")
        self.PSU1vSet = QLineEdit()
        self.VsetNumber=QLabel()
        self.Vset=self.aim1.queryVoltage()
        self.VsetNumber.setText("V Set Value: "+f"{self.Vset:.2f}"+" V")
        self.VsetNumber.setFrameShape(QFrame.StyledPanel)
        self.setVButton_PSU1 = QPushButton("Set Voltage")
        self.setVButton_PSU1.clicked.connect(self.on_vbutton_PSU1_clicked)

        self.Vlayout_PSU1.addWidget(self.VmeasNumber)
        self.Vlayout_PSU1.addWidget(self.PSU1vPrompt)
        self.Vlayout_PSU1.addWidget(self.VsetNumber)
        self.Vlayout_PSU1.addWidget(self.PSU1vSet)
        self.Vlayout_PSU1.addWidget(self.setVButton_PSU1)


    def create_Ibox_PSU1(self):
        self.Ibox_PSU1 = QGroupBox("Current")
        self.Ilayout_PSU1 = QVBoxLayout()
        self.Ibox_PSU1.setLayout(self.Ilayout_PSU1)

        self.PSU1iPrompt = QLabel("Current [A]")
        self.PSU1iSet = QLineEdit()
        self.IsetNumber=QLabel()
        self.Iset=self.aim1.queryCurrent()
        self.IsetNumber.setText("I Set Value: "+f"{self.Iset:.2f}"+" A")
        self.IsetNumber.setFrameShape(QFrame.StyledPanel)
        self.setIButton_PSU1 = QPushButton("Set Current")
        self.setIButton_PSU1.clicked.connect(self.on_ibutton_PSU1_clicked)

        self.Ilayout_PSU1.addWidget(self.ImeasNumber)
        self.Ilayout_PSU1.addWidget(self.PSU1iPrompt)
        self.Ilayout_PSU1.addWidget(self.IsetNumber)
        self.Ilayout_PSU1.addWidget(self.PSU1iSet)
        self.Ilayout_PSU1.addWidget(self.setIButton_PSU1)


    def create_Obox_PSU1(self):
        self.Obox_PSU1=QGroupBox("Output")
        self.Olayout_PSU1=QVBoxLayout()
        self.Obox_PSU1.setLayout(self.Olayout_PSU1)

        self.output_button_PSU1=QPushButton("Toggle Output")
        self.output_button_PSU1.clicked.connect(self.toggle_output_PSU1)
        self.Odisplay_PSU1=QLabel()
        self.Odisplay_PSU1.setAlignment(Qt.AlignCenter)
        self.Odisplay_PSU1.setFrameShape(QFrame.StyledPanel)

        if self.aim1.isOutputOn():
            self.Odisplay_PSU1.setText("Output is On")
            self.Odisplay_PSU1.setStyleSheet("background:limegreen")
        else:
            self.Odisplay_PSU1.setText("Output is Off")
            self.Odisplay_PSU1.setStyleSheet("background:red")

        self.Olayout_PSU1.addWidget(self.Odisplay_PSU1)
        self.Olayout_PSU1.addWidget(self.output_button_PSU1)

    def on_vbutton_PSU1_clicked(self):
        set_voltage = self.PSU1vSet.text()
        self.setV_PSU1(set_voltage)

    def setV_PSU1(self, set_voltage):
        if not self.aim1.isOutputOn():
            self.aim1.setVoltage(set_voltage)
        else:
            alert = QMessageBox()
            alert.setText("You must turn off output before changing the voltage")
            alert.exec_()

    def on_ibutton_PSU1_clicked(self):
        set_current = self.PSU1iSet.text()
        self.setI_PSU1(set_current)

    def setI_PSU1(self, set_current):
        if not self.aim1.isOutputOn():
            self.aim1.setCurrent(set_current)
        else:
            alert = QMessageBox()
            alert.setText("You must turn off output before changing the current")
            alert.exec_()

    def toggle_output_PSU1(self):
        if self.aim1.isOutputOn():
            self.aim1.outputOff()
        else:
            self.aim1.outputOn()

    def measure_voltage_PSU1(self):
        self.Vmeas = self.aim1.measureVoltage()
        self.VmeasNumber.display(f"{self.Vmeas:.2f}")

    def measure_current_PSU1(self):
        self.Imeas = self.aim1.measureCurrent()
        self.ImeasNumber.display(f"{self.Imeas:.2f}")

    def check_output_PSU1(self):
        if self.was_on_PSU1 != self.aim1.isOutputOn(): ## asking if anything has changed since last 0.5s, so we don't have to keep reprinting text
            self.was_on_PSU1=self.aim1.isOutputOn()
            if self.aim1.isOutputOn():
                self.Odisplay_PSU1.setText("Output is On")
                self.Odisplay_PSU1.setStyleSheet("background:limegreen")
            else:
                self.Odisplay_PSU1.setText("Output is Off")
                self.Odisplay_PSU1.setStyleSheet("background:red")

    def query_voltage_PSU1(self):
        if self.aim1.queryVoltage() != self.Vset:
            self.Vset=self.aim1.queryVoltage()
            self.VsetNumber.setText("V Set Value: "+f"{self.Vset:.2f}"+" V")

    def query_current_PSU1(self):
        if self.aim1.queryCurrent() != self.Iset:
            self.Iset=self.aim1.queryCurrent()
            self.IsetNumber.setText("I Set Value: "+f"{self.Iset:.2f}"+" A")

