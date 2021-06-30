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

from dcps import AimTTiEL302P
from dcps import AimTTiCPX400DP


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

        # start a timer to measure the PSU I and V every 0.5 s 
        self.qTimer = QTimer()
        self.qTimer.setInterval(500)
        self.qTimer.start()

        # start with a grid layout
        mainLayout = QGridLayout()
        
        # build a PSUBox
        #### some renaming in this function may be necessary as we build the GUI up to include other elements
        self.createPSU1Box()
        self.createPSU2Box()

        # add the PSUBox to the main layout (for now, it's the only element)
        mainLayout.addWidget(self.PSU1Box,0,0)
        mainLayout.addWidget(self.PSU2Box,0,1)

        # set the layout of the widget gallery to mainLayout
        self.setLayout(mainLayout)

    def createPSU1Box(self):
        
        # connect to the PSU
        self.aim1 = AimTTiEL302P('ASRL/dev/psu1::INSTR')
        self.aim1.open()

        # create the displays for the measurements of I and V
        self.VmeasNumber = QLCDNumber()
        self.VmeasNumber.setSegmentStyle(QLCDNumber.Flat)
        self.Vmeas = self.aim1.measureVoltage()

        self.ImeasNumber = QLCDNumber()
        self.ImeasNumber.setSegmentStyle(QLCDNumber.Flat)
        self.Imeas = self.aim1.measureCurrent()


        self.was_on_PSU1=self.aim1.isOutputOn()

        self.qTimer.timeout.connect(self.measure_voltage_PSU1)
        self.qTimer.timeout.connect(self.measure_current_PSU1)
        self.qTimer.timeout.connect(self.check_output_PSU1)


        ##Creates a PSU Box, calls functions to create the Vbox and Ibox that go inside.
        
        self.PSU1Box = QGroupBox("Control Single PSU")
        self.PSU1Box.setObjectName("psu1")
        self.PSU1Box.setStyleSheet("QGroupBox#psu1 { font-weight: bold; }")

        self.PSU1Layout = QGridLayout()
        self.PSU1Box.setLayout(self.PSU1Layout)
        
        self.create_Vbox_PSU1()
        self.create_Ibox_PSU1()
        self.PSU1Layout.addWidget(self.Vbox_PSU1,0,0)
        self.PSU1Layout.addWidget(self.Ibox_PSU1,0,1)

        self.create_Obox_PSU1()
        self.PSU1Layout.addWidget(self.Obox_PSU1,1,0)

    def create_Vbox_PSU1(self):
        self.Vbox_PSU1 = QGroupBox("Voltage")
        self.Vlayout_PSU1 = QVBoxLayout()
        self.Vbox_PSU1.setLayout(self.Vlayout_PSU1)
        
        self.PSU1vPrompt = QLabel("PSU 1 Voltage [V]")
        self.PSU1vSet = QLineEdit()
        
        self.setVButton_PSU1 = QPushButton("Set Voltage")
        self.setVButton_PSU1.clicked.connect(self.on_vbutton_PSU1_clicked)
        
        self.Vlayout_PSU1.addWidget(self.VmeasNumber)
        self.Vlayout_PSU1.addWidget(self.PSU1vPrompt)
        self.Vlayout_PSU1.addWidget(self.PSU1vSet)
        self.Vlayout_PSU1.addWidget(self.setVButton_PSU1)

    
    def create_Ibox_PSU1(self):
        self.Ibox_PSU1 = QGroupBox("Current")
        self.Ilayout_PSU1 = QVBoxLayout()
        self.Ibox_PSU1.setLayout(self.Ilayout_PSU1)

        self.PSU1iPrompt = QLabel("PSU 1 Current [A]")
        self.PSU1iSet = QLineEdit()

        self.setIButton_PSU1 = QPushButton("Set Current")
        self.setIButton_PSU1.clicked.connect(self.on_ibutton_PSU1_clicked)
        
        self.Ilayout_PSU1.addWidget(self.ImeasNumber)
        self.Ilayout_PSU1.addWidget(self.PSU1iPrompt)
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
            self.Odisplay_PSU1.setStyleSheet("background:green")
        else:
            self.Odisplay_PSU1.setText("Output is Off")
            self.Odisplay_PSU1.setStyleSheet("background:red")

        self.Olayout_PSU1.addWidget(self.Odisplay_PSU1)
        self.Olayout_PSU1.addWidget(self.output_button_PSU1)

    def on_vbutton_PSU1_clicked(self):
        set_voltage = self.PSU1vSet.text()
        self.setV_PSU1(set_voltage)

    def setV_PSU1(self, set_voltage):
        if not dry_run:
            if not self.aim1.isOutputOn():
                self.aim1.setVoltage(set_voltage)
            else:
                alert = QMessageBox()
                alert.setText("You must turn off output before changing the voltage")
                alert.exec_()
        else:
            print("Pranked! I didn't actually do it because you wanted a dry run.")

    def on_ibutton_PSU1_clicked(self):
        set_current = self.PSU1iSet.text()
        self.setI_PSU1(set_current)

    def setI_PSU1(self, set_current):
        if not dry_run:
            if not self.aim1.isOutputOn():
                self.aim1.setCurrent(set_current)
            else:
                alert = QMessageBox()
                alert.setText("You must turn off output before changing the current")
                alert.exec_()
        else:
            print("Pranked! I didn't actually do it because you wanted a dry run.")

    """
    # if "Toggle output" button pressed, then toggle the output
    def on_output_clicked(self):
        outputOn = self.aim.isOutputOn()
        # once the output box is showing up, all of this is kinda redundant bc you will already know the status of the output
        output_str = "on" if outputOn else "off"
        new_output_str = "off" if outputOn else "on"
        trigger_msg = QMessageBox.question(None,"Confirming action",f"Output is {output_str}, do you wish to turn it {new_output_str}?", QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)

        if trigger_msg == QMessageBox.Yes:
            self.toggle_output()
    """

    def toggle_output_PSU1(self):
        if not dry_run:
            if self.aim1.isOutputOn():
                self.aim1.outputOff()
            else:
                self.aim1.outputOn()
        else:
            print("Pranked! I didn't actually do it because you wanted a dry run.")

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
                self.Odisplay_PSU1.setStyleSheet("background:green")
            else:
                self.Odisplay_PSU1.setText("Output is Off")
                self.Odisplay_PSU1.setStyleSheet("background:red")






    def createPSU2Box(self):
        self.aim2=AimTTiCPX400DP('ASRL/dev/ttyACM1::INSTR')
        self.aim2.open()
        
        self.was_VTracking=self.aim2.isVTracking()
        #self.wasLock=self.aim2.isRemoteLock()

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

        #self.qTimer.timeout.connect(self.check_VTracking)
        #self.qTimer.timeout.connect(self.check_remoteLock)
        
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
        self.box1layout.addWidget(self.Obox1,1,0)
    
    def create_box2(self):

        self.box2=QGroupBox("Control Secondary PS")

        self.create_Vbox2()
        self.create_Ibox2()
        self.create_Obox2()

        self.box2layout=QGridLayout()
        self.box2.setLayout(self.box2layout)

        self.box2layout.addWidget(self.Vbox2,0,0)
        self.box2layout.addWidget(self.Ibox2,0,1)
        self.box2layout.addWidget(self.Obox2,1,0)
    
    def create_controlBox(self):

        self.controlBox=QGroupBox()
        
        self.create_OAllBox()
        #self.create_RemBox()
        self.create_trackingBox()

        self.controlLayout=QGridLayout()
        self.controlBox.setLayout(self.controlLayout)

        self.controlLayout.addWidget(self.OAllBox,0,0)
        #self.controlLayout.addWidget(self.remBox,1,0)
        self.controlLayout.addWidget(self.VTrackBox,2,0)

    def create_OAllBox(self):
        
        self.OAllBox = QGroupBox("Master Output")
        self.OAllLayout = QVBoxLayout()
        self.OAllBox.setLayout(self.OAllLayout)

        self.OAllButton = QPushButton("Toggle Master Output")
        self.OAllButton.clicked.connect(self.toggle_outputs_all)

        self.OAllLayout.addWidget(self.OAllButton)

    """def create_RemBox(self):

        self.remBox=QGroupBox("Remote Lock")
        self.remLayout=QVBoxLayout()
        self.remBox.setLayout(self.remLayout)
        
        self.remButton=QPushButton("Toggle Remote Lock")
        self.remButton.clicked.connect(self.toggle_remoteLock)

        self.remDisplay=QLabel()

        self.remDisplay.setAlignment(Qt.AlignCenter)
        self.remDisplay.setFrameShape(QFrame.StyledPanel)

        if self.aim2.isRemoteLock():
            self.remDisplay.setText("Remote Lock is On")
            self.remDisplay.setStyleSheet("background:green")
        else:
            self.remDisplay.setText("Remote Lock is Off")
            self.remDisplay.setStyleSheet("background:red")

        self.remLayout.addWidget(self.remDisplay)
        self.remLayout.addWidget(self.remButton)
        """

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
            self.VTdisplay.setStyleSheet("background:green")
        else:
            self.VTdisplay.setText("Voltage Tracking is Off")
            self.VTdisplay.setStyleSheet("background:red")

        self.VTlayout.addWidget(self.VTdisplay)
        self.VTlayout.addWidget(self.VTrackButton)
        

    """def toggle_remoteLock(self):
        if not dry_run:
            if self.aim2.isRemoteLock():
                self.aim2.setRemoteUnLock()
            else:
                self.aim2.setRemoteLock()
        else:
            print("Pranked! I didn't actually do it because you wanted a dry run.")

    def check_remoteLock(self):
        if self.wasLock != self.aim2.isRemoteLock():
            if self.aim2.isRemoteLock():
                self.remDisplay.setText("Remote Lock is On")
                self.remDisplay.setStyleSheet("background:green")
            else:
                self.remDisplay.setText("Remote Lock is Off")
                self.remDisplay.setStyleSheet("background:red")
        """

    def toggle_outputs_all(self):
        if not dry_run:
            if self.aim2.isOutputOn(1):
                self.aim2.outputOffAll()
            else:
                self.aim2.outputOn(1)
                self.aim2.outputOnAll()
        else:
            print("Pranked! I didn't actually do it because you wanted a dry run.")

    def toggle_VTracking(self):
        if not dry_run:
            if self.aim2.isVTracking():
                self.aim2.setIndependent()
            else:
                self.aim2.setVTracking()
        else:
            print("Pranked! I didn't actually do it because you wanted a dry run.")

    def check_VTracking(self):
        if self.was_VTracking != self.aim2.isVTracking():
            self.was_VTracking=self.aim2.isVTracking()
            if self.aim2.isVTracking():
                self.VTdisplay.setText("Voltage Tracking is Off")
                self.VTdisplay.setStyleSheet("background:red")
            else:
                self.VTdisplay.setText("Voltage Tracking is On")
                self.VTdisplay.setStyleSheet("background:green")
        

    def create_Vbox1(self):
        self.Vbox1 = QGroupBox("Voltage")
        self.Vlayout1 = QVBoxLayout()
        self.Vbox1.setLayout(self.Vlayout1)

        self.PSU2v1Prompt = QLabel("PSU 1 Voltage [V]")
        self.PSU2v1Set = QLineEdit()

        self.setVButton1 = QPushButton("Set Voltage")
        self.setVButton1.clicked.connect(self.on_vbutton1_clicked)

        self.Vlayout1.addWidget(self.VmeasNum1)
        self.Vlayout1.addWidget(self.PSU2v1Prompt)
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

        self.Vlayout2.addWidget(self.VmeasNum2)
        self.Vlayout2.addWidget(self.PSU2v2Prompt)
        self.Vlayout2.addWidget(self.PSU2v2Set)
        self.Vlayout2.addWidget(self.setVButton2)

    def create_Ibox1(self):
        self.Ibox1 = QGroupBox("Current")
        self.Ilayout1 = QVBoxLayout()
        self.Ibox1.setLayout(self.Ilayout1)

        self.PSU2i1Prompt = QLabel("PSU 1 Current [A]")
        self.PSU2i1Set = QLineEdit()

        self.setIButton1 = QPushButton("Set Current")
        self.setIButton1.clicked.connect(self.on_ibutton1_clicked)

        self.Ilayout1.addWidget(self.ImeasNum1)
        self.Ilayout1.addWidget(self.PSU2i1Prompt)
        self.Ilayout1.addWidget(self.PSU2i1Set)
        self.Ilayout1.addWidget(self.setIButton1)


    def create_Ibox2(self):
        self.Ibox2 = QGroupBox("Current")
        self.Ilayout2 = QVBoxLayout()
        self.Ibox2.setLayout(self.Ilayout2)

        self.PSU2i2Prompt = QLabel("PSU 2 Current [A]")
        self.PSU2i2Set = QLineEdit()

        self.setIButton2 = QPushButton("Set Current")
        self.setIButton2.clicked.connect(self.on_ibutton2_clicked)

        self.Ilayout2.addWidget(self.ImeasNum2)
        self.Ilayout2.addWidget(self.PSU2i2Prompt)
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
            self.Odisplay1.setStyleSheet("background:green")
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
            self.Odisplay2.setStyleSheet("background:green")
        else:
            self.Odisplay2.setText("Output is Off")
            self.Odisplay2.setStyleSheet("background:red")

        self.Olayout2.addWidget(self.Odisplay2)
        self.Olayout2.addWidget(self.output_button2)

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

    def setI(self, set_current, n):
        if not dry_run:
            if not self.aim2.isOutputOn(n):
                self.aim2.setCurrent(set_current,n)
            else:
                alert = QMessageBox()
                alert.setText("You must turn off output before changing the current")
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
                self.Odisplay1.setStyleSheet("background:green")
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
                self.Odisplay2.setStyleSheet("background:green")
            else:
                self.Odisplay2.setText("Output is Off")
                self.Odisplay2.setStyleSheet("background:red")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wg=WidgetGallery()
    wg.show()
    sys.exit(app.exec_())

