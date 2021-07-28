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

from dcps import AimTTiCPX400DP


class PSU2(QDialog):
    def __init__(self, parent=None):
        super(PSU2, self).__init__(parent)

        # start a timer to measure the PSU I and V every 0.5 s
        self.qTimer = QTimer()
        self.qTimer.setInterval(500)
        self.qTimer.start()

        mainLayout = QGridLayout()

        self.createPSU2Box()

        self.setLayout(mainLayout)
        mainLayout.addWidget(self.PSU2Box,0,0)

    def createPSU2Box(self):
        self.aim2=AimTTiCPX400DP('ASRL/dev/ttyACM1::INSTR')
        self.aim2.open()

        self.was_VTracking=self.aim2.isVTracking()

        self.VmeasNum1 = QLCDNumber()
        self.VmeasNum1.setSegmentStyle(QLCDNumber.Flat)
        self.Vmeas1 = self.aim2.measureVoltage(1)
        self.ImeasNum1 = QLCDNumber()
        self.ImeasNum1.setSegmentStyle(QLCDNumber.Flat)
        self.Imeas1 = self.aim2.measureCurrent(1)
        self.O1_was_on=self.aim2.isOutputOn(1)

        self.VmeasNum2 = QLCDNumber()
        self.VmeasNum2.setSegmentStyle(QLCDNumber.Flat)
        self.Vmeas2 = self.aim2.measureVoltage(2)
        self.ImeasNum2 = QLCDNumber()
        self.ImeasNum2.setSegmentStyle(QLCDNumber.Flat)
        self.Imeas2 = self.aim2.measureCurrent(2)
        self.O2_was_on=self.aim2.isOutputOn(2)

        self.qTimer.timeout.connect(self.check_VTracking)
        self.qTimer.timeout.connect(self.query_voltage1)
        self.qTimer.timeout.connect(self.query_current1)
        self.qTimer.timeout.connect(self.query_voltage2)
        self.qTimer.timeout.connect(self.query_current2)
        self.qTimer.timeout.connect(self.measure_voltage1)
        self.qTimer.timeout.connect(self.measure_current1)
        self.qTimer.timeout.connect(self.check_output1)
        self.qTimer.timeout.connect(self.measure_voltage2)
        self.qTimer.timeout.connect(self.measure_current2)
        self.qTimer.timeout.connect(self.check_output2)

        self.PSU2Box = QGroupBox("Control Double PSU")
        self.PSU2Box.setObjectName("psu2")
        self.PSU2Box.setStyleSheet("QGroupBox#psu2 { font-weight: bold; }")
        self.PSU2Layout = QGridLayout()
        self.PSU2Box.setLayout(self.PSU2Layout)

        self.create_box1()
        self.create_box2()
        self.create_controlBox()

        self.PSU2Layout.addWidget(self.controlBox,0,0)
        self.PSU2Layout.addWidget(self.box1,0,1)
        self.PSU2Layout.addWidget(self.box2,0,2)

    def create_box1(self):
        self.box1=QGroupBox("Control Main PS")
        self.create_Vbox1()
        self.create_Ibox1()
        self.create_Obox1()
        self.box1layout=QGridLayout()
        self.box1.setLayout(self.box1layout)
        self.box1layout.addWidget(self.Vbox1,0,0)
        self.box1layout.addWidget(self.Ibox1,0,1)
        self.box1layout.addWidget(self.Obox1,1,0,1,2)

    def create_box2(self):
        self.box2=QGroupBox("Control Secondary PS")
        self.create_Vbox2()
        self.create_Ibox2()
        self.create_Obox2()
        self.box2layout=QGridLayout()
        self.box2.setLayout(self.box2layout)
        self.box2layout.addWidget(self.Vbox2,0,0)
        self.box2layout.addWidget(self.Ibox2,0,1)
        self.box2layout.addWidget(self.Obox2,1,0,1,2)

    def create_controlBox(self):
        self.controlBox=QGroupBox()
        self.create_OAllBox()
        self.create_trackingBox()
        self.controlLayout=QGridLayout()
        self.controlBox.setLayout(self.controlLayout)
        self.controlLayout.addWidget(self.OAllBox,0,0)
        self.controlLayout.addWidget(self.VTrackBox,1,0)

    def create_OAllBox(self):
        self.OAllBox = QGroupBox("Master Output")
        self.OAllLayout = QVBoxLayout()
        self.OAllBox.setLayout(self.OAllLayout)
        self.OAllButton = QPushButton("Toggle Master Output")
        self.OAllButton.clicked.connect(self.toggle_outputs_all)
        self.OAllLayout.addWidget(self.OAllButton)

    def create_trackingBox(self):
        self.VTrackBox=QGroupBox("Voltage Tracking")
        self.VTlayout=QVBoxLayout()
        self.VTrackBox.setLayout(self.VTlayout)

        self.VTrackButton=QPushButton("Toggle Voltage Tracking")
        self.VTrackButton.clicked.connect(self.toggle_VTracking)
        self.VTdisplay=QLabel()
        self.VTdisplay.setAlignment(Qt.AlignCenter)
        self.VTdisplay.setFrameShape(QFrame.StyledPanel)

        if self.aim2.isVTracking():
            self.VTdisplay.setText("Voltage Tracking is On")
            self.VTdisplay.setStyleSheet("background:limegreen")
        else:
            self.VTdisplay.setText("Voltage Tracking is Off")
            self.VTdisplay.setStyleSheet("background:red")

        self.VTlayout.addWidget(self.VTdisplay)
        self.VTlayout.addWidget(self.VTrackButton)

    def toggle_outputs_all(self):
        if self.aim2.isOutputOn(1):
            self.aim2.outputOffAll()
        else:
            self.aim2.outputOn(1)
            self.aim2.outputOnAll()

    def toggle_VTracking(self):
        if not self.aim2.isOutputOn(2):
            if self.aim2.isVTracking():
                self.aim2.setIndependent()
            else:
                self.aim2.setVTracking()
        else:
            alert=QMessageBox()
            alert.setText("You must turn off output 2 before toggling voltage tracking.")
            alert.exec_()

    def check_VTracking(self):
        if self.was_VTracking != self.aim2.isVTracking():
            self.was_VTracking=self.aim2.isVTracking()
            if not self.aim2.isVTracking():
                self.VTdisplay.setText("Voltage Tracking is Off")
                self.VTdisplay.setStyleSheet("background:red")
            else:
                self.VTdisplay.setText("Voltage Tracking is On")
                self.VTdisplay.setStyleSheet("background:limegreen")


    def create_Vbox1(self):
        self.Vbox1 = QGroupBox("Voltage")
        self.Vlayout1 = QVBoxLayout()
        self.Vbox1.setLayout(self.Vlayout1)

        self.PSU2v1Prompt = QLabel("PSU 1 Voltage [V]")
        self.PSU2v1Set = QLineEdit()
        self.setVButton1 = QPushButton("Set Voltage")
        self.setVButton1.clicked.connect(self.on_vbutton1_clicked)
        self.V1setNum=QLabel()
        self.V1set=self.aim2.queryVoltage(1)
        self.V1setNum.setText("V Set Value: "+f"{self.V1set:.2f}"+" V")
        self.V1setNum.setFrameShape(QFrame.StyledPanel)

        self.Vlayout1.addWidget(self.VmeasNum1)
        self.Vlayout1.addWidget(self.PSU2v1Prompt)
        self.Vlayout1.addWidget(self.V1setNum)
        self.Vlayout1.addWidget(self.PSU2v1Set)
        self.Vlayout1.addWidget(self.setVButton1)

    def create_Vbox2(self):
        self.Vbox2 = QGroupBox("Voltage")
        self.Vlayout2 = QVBoxLayout()
        self.Vbox2.setLayout(self.Vlayout2)

        self.PSU2v2Prompt = QLabel("PSU 2 Voltage [V]")
        self.PSU2v2Set = QLineEdit()
        self.setVButton2 = QPushButton("Set Voltage")
        self.setVButton2.clicked.connect(self.on_vbutton2_clicked)
        self.V2setNum=QLabel()
        self.V2set=self.aim2.queryVoltage(2)
        self.V2setNum.setText("V Set Value: "+f"{self.V2set:.2f}"+" V")
        self.V2setNum.setFrameShape(QFrame.StyledPanel)

        self.Vlayout2.addWidget(self.VmeasNum2)
        self.Vlayout2.addWidget(self.PSU2v2Prompt)
        self.Vlayout2.addWidget(self.V2setNum)
        self.Vlayout2.addWidget(self.PSU2v2Set)
        self.Vlayout2.addWidget(self.setVButton2)

    def create_Ibox1(self):
        self.Ibox1 = QGroupBox("Current")
        self.Ilayout1 = QVBoxLayout()
        self.Ibox1.setLayout(self.Ilayout1)

        self.PSU2i1Prompt = QLabel("PSU 1 Current [A]")
        self.PSU2i1Set = QLineEdit()
        self.I1setNum=QLabel()
        self.I1set=self.aim2.queryCurrent(1)
        self.I1setNum.setText("I Set Value: "+f"{self.I1set:.2f}"+" A")
        self.I1setNum.setFrameShape(QFrame.StyledPanel)
        self.setIButton1 = QPushButton("Set Current")
        self.setIButton1.clicked.connect(self.on_ibutton1_clicked)

        self.Ilayout1.addWidget(self.ImeasNum1)
        self.Ilayout1.addWidget(self.PSU2i1Prompt)
        self.Ilayout1.addWidget(self.I1setNum)
        self.Ilayout1.addWidget(self.PSU2i1Set)
        self.Ilayout1.addWidget(self.setIButton1)


    def create_Ibox2(self):
        self.Ibox2 = QGroupBox("Current")
        self.Ilayout2 = QVBoxLayout()
        self.Ibox2.setLayout(self.Ilayout2)

        self.PSU2i2Prompt = QLabel("PSU 2 Current [A]")
        self.PSU2i2Set = QLineEdit()
        self.I2setNum=QLabel()
        self.I2set=self.aim2.queryCurrent(2)
        self.I2setNum.setText("I Set Value: "+f"{self.I2set:.2f}"+" A")
        self.I2setNum.setFrameShape(QFrame.StyledPanel)
        self.setIButton2 = QPushButton("Set Current")
        self.setIButton2.clicked.connect(self.on_ibutton2_clicked)

        self.Ilayout2.addWidget(self.ImeasNum2)
        self.Ilayout2.addWidget(self.PSU2i2Prompt)
        self.Ilayout2.addWidget(self.I2setNum)
        self.Ilayout2.addWidget(self.PSU2i2Set)
        self.Ilayout2.addWidget(self.setIButton2)


    def create_Obox1(self):
        self.Obox1=QGroupBox("Output")
        self.Olayout1=QVBoxLayout()
        self.Obox1.setLayout(self.Olayout1)

        self.output_button1=QPushButton("Toggle Output")
        self.output_button1.clicked.connect(lambda: self.toggle_output(1))
        self.Odisplay1=QLabel()
        self.Odisplay1.setAlignment(Qt.AlignCenter)
        self.Odisplay1.setFrameShape(QFrame.StyledPanel)

        if self.aim2.isOutputOn(1):
            self.Odisplay1.setText("Output is On")
            self.Odisplay1.setStyleSheet("background:limegreen")
        else:
            self.Odisplay1.setText("Output is Off")
            self.Odisplay1.setStyleSheet("background:red")

        self.Olayout1.addWidget(self.Odisplay1)
        self.Olayout1.addWidget(self.output_button1)

    def create_Obox2(self):
        self.Obox2=QGroupBox("Output")
        self.Olayout2=QVBoxLayout()
        self.Obox2.setLayout(self.Olayout2)

        self.output_button2=QPushButton("Toggle Output")
        self.output_button2.clicked.connect(lambda: self.toggle_output(2))
        self.Odisplay2=QLabel()
        self.Odisplay2.setAlignment(Qt.AlignCenter)
        self.Odisplay2.setFrameShape(QFrame.StyledPanel)

        if self.aim2.isOutputOn(2):
            self.Odisplay2.setText("Output is On")
            self.Odisplay2.setStyleSheet("background:limegreen")
        else:
            self.Odisplay2.setText("Output is Off")
            self.Odisplay2.setStyleSheet("background:red")

        self.Olayout2.addWidget(self.Odisplay2)
        self.Olayout2.addWidget(self.output_button2)



    def setV(self, set_voltage, channel):
        if not self.aim2.isOutputOn(channel):
            self.aim2.setVoltage(set_voltage,channel)
        else:
            alert = QMessageBox()
            alert.setText("You must turn off output before changing the voltage")
            alert.exec_()

    def setI(self,set_current,channel):
        if not self.aim2.isOutputOn(channel):
            self.aim2.setCurrent(set_current,channel)
        else:
            alert = QMessageBox()
            alert.setText("You must turn off output before changing the current")
            alert.exec_()

    def toggle_output(self,channel):
        if self.aim2.isOutputOn(channel):
            self.aim2.outputOff(channel)
        else:
            self.aim2.outputOn(channel)

    def on_vbutton1_clicked(self):
        set_voltage = self.PSU2v1Set.text()
        self.setV(set_voltage,1)

    def on_vbutton2_clicked(self):
        set_voltage = self.PSU2v2Set.text()
        self.setV(set_voltage,2)

    def on_ibutton1_clicked(self):
        set_current = self.PSU2i1Set.text()
        self.setI(set_current,1)

    def on_ibutton2_clicked(self):
        set_current = self.PSU2i2Set.text()
        self.setI(set_current,2)

    def measure_voltage1(self):
        self.Vmeas1 = self.aim2.measureVoltage(1)
        self.VmeasNum1.display(f"{self.Vmeas1:.2f}")

    def measure_current1(self):
        self.Imeas1 = self.aim2.measureCurrent(1)
        self.ImeasNum1.display(f"{self.Imeas1:.2f}")

    def check_output1(self):
        if self.O1_was_on != self.aim2.isOutputOn(1): ## asking if anything has changed since last 0.5s, so we don't have to keep reprinting text
            self.O1_was_on=self.aim2.isOutputOn(1)
            if self.aim2.isOutputOn(1):
                self.Odisplay1.setText("Output is On")
                self.Odisplay1.setStyleSheet("background:limegreen")
            else:
                self.Odisplay1.setText("Output is Off")
                self.Odisplay1.setStyleSheet("background:red")

    def measure_voltage2(self):
        self.Vmeas2 = self.aim2.measureVoltage(2)
        self.VmeasNum2.display(f"{self.Vmeas2:.2f}")

    def measure_current2(self):
        self.Imeas2 = self.aim2.measureCurrent(2)
        self.ImeasNum2.display(f"{self.Imeas2:.2f}")

    def check_output2(self):
        if self.O2_was_on != self.aim2.isOutputOn(2): ## asking if anything has changed since last 0.5s, so we don't have to keep reprinting text
            self.O2_was_on=self.aim2.isOutputOn(2)
            if self.aim2.isOutputOn(2):
                self.Odisplay2.setText("Output is On")
                self.Odisplay2.setStyleSheet("background:limegreen")
            else:
                self.Odisplay2.setText("Output is Off")
                self.Odisplay2.setStyleSheet("background:red")

    def query_voltage1(self):
        if self.aim2.queryVoltage(1) != self.V1set:
            self.V1set=self.aim2.queryVoltage(1)
            self.V1setNum.setText("V Set Value: "+f"{self.V1set:.2f}"+" V")

    def query_current1(self):
        if self.aim2.queryCurrent(1) != self.I1set:
            self.I1set=self.aim2.queryCurrent(1)
            self.I1setNum.setText("I Set Value: "+f"{self.I1set:.2f}"+" A")

    def query_voltage2(self):
        if self.aim2.queryVoltage(2) != self.V2set:
            self.V2set=self.aim2.queryVoltage(2)
            self.V2setNum.setText("V Set Value: "+f"{self.V2set:.2f}"+" V")

    def query_current2(self):
        if self.aim2.queryCurrent(2) != self.I2set:
            self.I2set=self.aim2.queryCurrent(2)
            self.I2setNum.setText("I Set Value: "+f"{self.I2set:.2f}"+" A")

