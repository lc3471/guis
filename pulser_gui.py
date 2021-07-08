#!/usr/env/bin python
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 14:06:41 2019

@author: colin adams :^)

"""
# TODO add auto-updating (0.5 s period?) elements that show the results of polling:
#### the set voltage/current (queryVoltage/Current)
#### the output status (isOutputOn)
# TODO expand the GUI to incorporate:
#### other PSUs
#### the function generator
# TODO logging


from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLCDNumber,
        QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QMessageBox)
#import serial
#import time
import sys
import argparse

from dcps import RigolDG5000

import struct
import functools

from datetime import datetime

parser=argparse.ArgumentParser()
parser.add_argument('--dry_run',
                        type=bool,
                        default=False,
                        help='Run without controlling the flasher (default=False)')
args = parser.parse_args()

chr = functools.partial(struct.pack,'B')

windows_system = False
dry_run = args.dry_run

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        # start a timer ?? 
        self.qTimer = QTimer()
        self.qTimer.setInterval(500)
        self.qTimer.start()
        
        self.qTimer.timeout.connect(self.check_output)
        self.qTimer.timeout.connect(self.check_pulse)

        # start with a grid layout
        mainLayout = QGridLayout()
        
        # build a PSUBox
        #### some renaming in this function may be necessary as we build the GUI up to include other elements
        
        self.create_pulser_box()
        mainLayout.addWidget(self.pulser_box,0,0)

        # set the layout of the widget gallery to mainLayout
        self.setLayout(mainLayout)

    def create_pulser_box(self):
        
        self.Rigol=RigolDG5000('USB0::6833::1600::DG5T220100004\x00::0::INSTR')

        self.pulser_box=QGroupBox("Rigol Pulser")
        self.pulser_layout=QGridLayout()
        self.pulser_box.setLayout(self.pulser_layout)
        
        self.create_box1()
        self.pulser_layout.addWidget(self.box1,0,0)
        self.create_box2()
        self.pulser_layout.addWidget(self.box2,0,1)

    def create_box1(self):

        self.box1=QGroupBox("Channel 1")
        self.box1layout=QGridLayout()
        self.box1.setLayout(self.box1layout)

        self.create_Obox1()
        self.create_Pbox1()

        self.box1layout.addWidget(self.Obox1)
        self.box1layout.addWidget(self.Pbox1)

    def create_box2(self):

        self.box2=QGroupBox("Channel 2")
        self.box2layout=QGridLayout()
        self.box2.setLayout(self.box2layout)

        self.create_Obox2()
        self.create_Pbox2()

        self.box2layout.addWidget(self.Obox2)
        self.box2layout.addWidget(self.Pbox2)

    def create_Obox1(self):

        self.Obox1=QGroupBox("Output")
        self.Olayout1=QVBoxLayout()
        self.Obox1.setLayout(self.Olayout1)

        self.Obutton1=QPushButton("Toggle Output")
        self.Obutton1.clicked.connect(lambda: self.toggle_output(1))

        self.Odisplay1=QLabel()

        self.Odisplay1.setAlignment(Qt.AlignCenter)
        self.Odisplay1.setFrameShape(QFrame.StyledPanel)
        
        self.was_on1=self.Rigol.isOutputOn(1)

        if self.was_on1:
            self.Odisplay1.setText("Output 1 is On")
            self.Odisplay1.setStyleSheet("background:green")
        else:
            self.Odisplay1.setText("Output 1 is Off")
            self.Odisplay1.setStyleSheet("background:red")

        self.Olayout1.addWidget(self.Obutton1)
        self.Olayout1.addWidget(self.Odisplay1)

    def create_Obox2(self):

        self.Obox2=QGroupBox("Output")
        self.Olayout2=QVBoxLayout()
        self.Obox2.setLayout(self.Olayout2)

        self.Obutton2=QPushButton("Toggle Output")
        self.Obutton2.clicked.connect(lambda: self.toggle_output(2))

        self.Odisplay2=QLabel()

        self.Odisplay2.setAlignment(Qt.AlignCenter)
        self.Odisplay2.setFrameShape(QFrame.StyledPanel)

        self.was_on2=self.Rigol.isOutputOn(2)

        if self.was_on2:
            self.Odisplay2.setText("Output 2 is On")
            self.Odisplay2.setStyleSheet("background:green")
        else:
            self.Odisplay2.setText("Output 2 is Off")
            self.Odisplay2.setStyleSheet("background:red")

        self.Olayout2.addWidget(self.Obutton2)
        self.Olayout2.addWidget(self.Odisplay2)

    def create_Pbox1(self):

        self.Pbox1=QGroupBox("Pulse")
        self.Playout1=QGridLayout()
        self.Pbox1.setLayout(self.Playout1)

        self.create_freq1box()
        self.create_amp1box()
        self.create_os1box()
        self.create_delay1box()

        self.pulse1button=QPushButton("Send Pulse")
        self.pulse1button.clicked.connect(self.on_pulse1_clicked)

        self.Playout1.addWidget(self.freq1box,0,0)
        self.Playout1.addWidget(self.amp1box,0,1)
        self.Playout1.addWidget(self.os1box,1,0)
        self.Playout1.addWidget(self.delay1box,1,1)
        self.Playout1.addWidget(self.pulse1button,2,0,1,2)

    def create_Pbox2(self):

        self.Pbox2=QGroupBox("Pulse")
        self.Playout2=QGridLayout()
        self.Pbox2.setLayout(self.Playout2)

        self.create_freq2box()
        self.create_amp2box()
        self.create_os2box()
        self.create_delay2box()

        self.pulse2button=QPushButton("Send Pulse")
        self.pulse2button.clicked.connect(self.on_pulse2_clicked)

        self.Playout2.addWidget(self.freq2box,0,0)
        self.Playout2.addWidget(self.amp2box,0,1)
        self.Playout2.addWidget(self.os2box,1,0)
        self.Playout2.addWidget(self.delay2box,1,1)
        self.Playout2.addWidget(self.pulse2button,2,0,1,2)

    def create_freq1box(self):
        self.freq1box=QGroupBox("Frequency [Hz]")
        self.freq1layout=QVBoxLayout()
        self.freq1box.setLayout(self.freq1layout)

        self.freq1disp=QLCDNumber()
        self.freq1disp.setSegmentStyle(QLCDNumber.Flat)
        
        self.freq1setLabel=QLabel("Set Frequency")
        self.freq1set=QLineEdit()

        self.freq1layout.addWidget(self.freq1disp)
        self.freq1layout.addWidget(self.freq1setLabel)
        self.freq1layout.addWidget(self.freq1set)

    def create_amp1box(self):
        self.amp1box=QGroupBox("Amplitude [Vpp]")
        self.amp1layout=QVBoxLayout()
        self.amp1box.setLayout(self.amp1layout)

        self.amp1disp=QLCDNumber()
        self.amp1disp.setSegmentStyle(QLCDNumber.Flat)
        
        self.amp1setLabel=QLabel("Set Amplitude")
        self.amp1set=QLineEdit()

        self.amp1layout.addWidget(self.amp1disp)
        self.amp1layout.addWidget(self.amp1setLabel)
        self.amp1layout.addWidget(self.amp1set)

    def create_os1box(self):
        self.os1box=QGroupBox("Offset [Vdc]")
        self.os1layout=QVBoxLayout()
        self.os1box.setLayout(self.os1layout)

        self.os1disp=QLCDNumber()
        self.os1disp.setSegmentStyle(QLCDNumber.Flat)
        
        self.os1setLabel=QLabel("Set Offset")
        self.os1set=QLineEdit()

        self.os1layout.addWidget(self.os1disp)
        self.os1layout.addWidget(self.os1setLabel)
        self.os1layout.addWidget(self.os1set)

    def create_delay1box(self):
        self.delay1box=QGroupBox("Delay [s]")
        self.delay1layout=QVBoxLayout()
        self.delay1box.setLayout(self.delay1layout)

        self.delay1disp=QLCDNumber()
        self.delay1disp.setSegmentStyle(QLCDNumber.Flat)
        
        self.delay1setLabel=QLabel("Set Delay")
        self.delay1set=QLineEdit()

        self.delay1layout.addWidget(self.delay1disp)
        self.delay1layout.addWidget(self.delay1setLabel)
        self.delay1layout.addWidget(self.delay1set)

    def create_freq2box(self):
        self.freq2box=QGroupBox("Frequency [Hz]")
        self.freq2layout=QVBoxLayout()
        self.freq2box.setLayout(self.freq2layout)

        self.freq2disp=QLCDNumber()
        self.freq2disp.setSegmentStyle(QLCDNumber.Flat)

        self.freq2setLabel=QLabel("Set Frequency")
        self.freq2set=QLineEdit()

        self.freq2layout.addWidget(self.freq2disp)
        self.freq2layout.addWidget(self.freq2setLabel)
        self.freq2layout.addWidget(self.freq2set)

    def create_amp2box(self):
        self.amp2box=QGroupBox("Amplitude [Vpp]")
        self.amp2layout=QVBoxLayout()
        self.amp2box.setLayout(self.amp2layout)

        self.amp2disp=QLCDNumber()
        self.amp2disp.setSegmentStyle(QLCDNumber.Flat)

        self.amp2setLabel=QLabel("Set Amplitude")
        self.amp2set=QLineEdit()

        self.amp2layout.addWidget(self.amp2disp)
        self.amp2layout.addWidget(self.amp2setLabel)
        self.amp2layout.addWidget(self.amp2set)

    def create_os2box(self):
        self.os2box=QGroupBox("Offset [Vdc]")
        self.os2layout=QVBoxLayout()
        self.os2box.setLayout(self.os2layout)

        self.os2disp=QLCDNumber()
        self.os2disp.setSegmentStyle(QLCDNumber.Flat)

        self.os2setLabel=QLabel("Set Offset")
        self.os2set=QLineEdit()

        self.os2layout.addWidget(self.os2disp)
        self.os2layout.addWidget(self.os2setLabel)
        self.os2layout.addWidget(self.os2set)

    def create_delay2box(self):
        self.delay2box=QGroupBox("Delay [s]")
        self.delay2layout=QVBoxLayout()
        self.delay2box.setLayout(self.delay2layout)

        self.delay2disp=QLCDNumber()
        self.delay2disp.setSegmentStyle(QLCDNumber.Flat)

        self.delay2setLabel=QLabel("Set Delay")
        self.delay2set=QLineEdit()

        self.delay2layout.addWidget(self.delay2disp)
        self.delay2layout.addWidget(self.delay2setLabel)
        self.delay2layout.addWidget(self.delay2set)


    def toggle_output(self, channel=None):
        if not dry_run:
            if self.Rigol.isOutputOn(channel):
                self.Rigol.outputOff(channel)
            else:
                self.Rigol.outputOn(channel)
        else: 
            print("Pranked! dry run :)")

    def check_output(self):
        if self.was_on1 != self.Rigol.isOutputOn(1):
            self.was_on1=self.Rigol.isOutputOn(1)
            if self.was_on1:
                self.Odisplay1.setText("Output 1 is On")
                self.Odisplay1.setStyleSheet("background:green")
            else:
                self.Odisplay1.setText("Output 1 is Off")
                self.Odisplay1.setStyleSheet("background:red")
        
        if self.was_on2 != self.Rigol.isOutputOn(2):
            self.was_on2=self.Rigol.isOutputOn(2)
            if self.was_on2:
                self.Odisplay2.setText("Output 2 is On")
                self.Odisplay2.setStyleSheet("background:green")
            else:
                self.Odisplay2.setText("Output 2 is Off")
                self.Odisplay2.setStyleSheet("background:red")

    def on_pulse1_clicked(self):

        freq=self.freq1set.text()
        amp=self.amp1set.text()
        offset=self.os1set.text()
        delay=self.delay1set.text()
        channel=1

        self.Rigol.applyPulse(freq, amp, offset, delay, channel)

    def on_pulse2_clicked(self):

        freq=self.freq2set.text()
        amp=self.amp2set.text()
        offset=self.os2set.text()
        delay=self.delay2set.text()
        channel=2

        self.Rigol.applyPulse(freq, amp, offset, delay, channel)

    def check_pulse(self):

        lst1=self.Rigol.queryApply(1)
        lst2=self.Rigol.queryApply(2)
        self.freq1disp.display(f"{lst1[1]:.2f}")
        self.amp1disp.display(f"{lst1[2]:.2f}")
        self.os1disp.display(f"{lst1[3]:.2f}")
        self.delay1disp.display(f"{lst1[4]:.2f}")

        self.freq2disp.display(f"{lst2[1]:.2f}")
        self.amp2disp.display(f"{lst2[2]:.2f}")
        self.os2disp.display(f"{lst2[3]:.2f}")
        self.delay2disp.display(f"{lst2[4]:.2f}")




    """def createPSU2Box(self):
        self.aim2=AimTTiCPX400DP('ASRL/dev/ttyACM1::INSTR')
        self.aim2.open()
        
        self.was_VTracking=self.aim2.isVTracking()
        #self.wasLock=self.aim2.isRemoteLock()

        self.VmeasNum1 = QLCDNumber()
        self.VmeasNum1.setSegmentStyle(QLCDNumber.Flat)
        self.Vmeas1 = self.aim2.measureVoltage(1)

        self.O1_was_on=self.aim2.isOutputOn(1)

        self.qTimer.timeout.connect(self.check_VTracking)
        #self.qTimer.timeout.connect(self.check_remoteLock)
        
        self.qTimer.timeout.connect(self.query_voltage1)

        self.qTimer.timeout.connect(self.measure_voltage1)
        self.qTimer.timeout.connect(self.check_output1)

        self.PSU2Box = QGroupBox("Control Double PSU")
        self.PSU2Box.setObjectName("psu2")
        self.PSU2Box.setStyleSheet("QGroupBox#psu2 { font-weight: bold; }")

        self.PSU2Layout = QGridLayout()
        self.PSU2Box.setLayout(self.PSU2Layout)
        
        self.create_box1()
        self.create_controlBox()

        self.PSU2Layout.addWidget(self.controlBox,0,0)
        self.PSU2Layout.addWidget(self.box1,0,1)

    def create_box1(self):

        self.box1=QGroupBox("Control Main PS")


        self.create_Vbox1()
        self.create_Obox1()

        self.box1layout=QGridLayout()
        self.box1.setLayout(self.box1layout)

        self.box1layout.addWidget(self.Vbox1,0,0)
        self.box1layout.addWidget(self.Obox1,1,0)
    
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
            self.Odisplay1.setStyleSheet("background:green")
        else:
            self.Odisplay1.setText("Output is Off")
            self.Odisplay1.setStyleSheet("background:red")

        self.Olayout1.addWidget(self.Odisplay1)
        self.Olayout1.addWidget(self.output_button1)

    def setV(self, set_voltage, n):
        if not dry_run:
            if not self.aim2.isOutputOn(n):
                self.aim2.setVoltage(set_voltage,n)
            else:
                alert = QMessageBox()
                alert.setText("You must turn off output before changing the voltage")
                alert.exec_()
        else:
            print("Pranked! I didn't actually do it because you wanted a dry run.")

    def toggle_output(self, n):
        if not dry_run:
            if self.aim2.isOutputOn(n):
                self.aim2.outputOff(n)
            else:
                self.aim2.outputOn(n)
        else:
            print("Pranked! I didn't actually do it because you wanted a dry run.")

    def on_vbutton1_clicked(self):
        set_voltage = self.PSU2v1Set.text()
        self.setV(set_voltage,1)

    def measure_voltage1(self):
        self.Vmeas1 = self.aim2.measureVoltage(1)
        self.VmeasNum1.display(f"{self.Vmeas1:.2f}")

    def check_output1(self):
        if self.O1_was_on != self.aim2.isOutputOn(1): ## asking if anything has changed since last 0.5s, so we don't have to keep reprinting text
            self.O1_was_on=self.aim2.isOutputOn(1)
            if self.aim2.isOutputOn(1):
                self.Odisplay1.setText("Output is On")
                self.Odisplay1.setStyleSheet("background:green")
            else:
                self.Odisplay1.setText("Output is Off")
                self.Odisplay1.setStyleSheet("background:red")

    def query_voltage1(self):
        if self.aim2.queryVoltage(1) != self.V1set:
            self.V1set=self.aim2.queryVoltage(1)
            self.V1setNum.setText("V Set Value: "+f"{self.V1set:.2f}"+" V")
"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wg=WidgetGallery()
    wg.show()
    sys.exit(app.exec_())

