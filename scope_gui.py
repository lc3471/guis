# author: Laurel Carpenter
# date: 7/15/2021

"""
Troubleshooting:
visa not connecting to device:
-make sure device is actually connected using 'lsusb' command
-make sure '0660' permission is granted in usbtmc.rules
-when first turning on it takes ~30 sec to actually connect
'device has no langid':
-turn the scope off and on again, wait a few seconds to reconnect

This machine freaks out if it's queried too much, or if its responses are too
large. Avoid doing the following:
-adjusting tdiv/vdiv/ofst/trdl too much too quickly
-sampling too many points:
    tdiv 1-2 ns with sparsing=all works fine, but once it reaches 5 ns the
    number of sampled points is too high. set number of points to something like
     30, and adjust first point and sparsing to make sure you're getting the
    whole curve.

if you want to save a waveform but it's not working from the GUI, run
'scope_test.py' without running GUI.
"""


from PyQt5.QtChart import QChartView,QChart,QLineSeries,QSplineSeries,QValueAxis
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLCDNumber, QLineEdit,
    QPushButton, QVBoxLayout, QWidget, QMessageBox)
import visa
import math

import sys
import argparse

import struct
import functools

from datetime import datetime
from time import sleep
import numpy as np

import pandas as pd

chr = functools.partial(struct.pack,'B')
windows_system = False

fname='test'

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.wait=0.5
        self.open_siglent('USB0::62701::60986::SDS1ECDD2R8216::0::INSTR')

        self.qTimer=QTimer()
        self.qTimer.setInterval(1000)
        self.qTimer.start()
        self.qTimer.timeout.connect(self.check_acq)
        self.qTimer.timeout.connect(self.check_vdiv)
        self.qTimer.timeout.connect(self.check_ofst)
        self.qTimer.timeout.connect(self.check_tdiv)
        self.qTimer.timeout.connect(self.check_sara)
        self.qTimer.timeout.connect(self.check_waveform)

        mainLayout=QGridLayout()

        self.create_scope_box()
        mainLayout.addWidget(self.scope_box,0,0)

        self.setLayout(mainLayout)

    def create_scope_box(self):
        self.scope_box=QGroupBox("Siglent Oscilloscope")
        self.scope_layout=QHBoxLayout()
        self.scope_box.setLayout(self.scope_layout)

        # 2 boxes for 2 channels

        self.create_stats_box()
        self.scope_layout.addWidget(self.stats_box)

        try:
            self.create_box1()
            self.channel1=True
            self.scope_layout.addWidget(self.box1)
        except:
            self.channel1=False
        """try:
            self.create_box2()
            self.channel2=True
            self.scope_layout.addWidget(self.box2)
        except:
            self.channel2=False"""
        self.channel2=False

    def create_stats_box(self):
        self.stats_box=QGroupBox()
        self.stats_layout=QGridLayout()
        self.stats_box.setLayout(self.stats_layout)

        tdiv_label=QLabel("Time Division [s]")
        self.tdiv_disp=QLCDNumber()
        self.tdiv=self.query_tdiv()
        self.tdiv_disp.display(self.tdiv)
        sara_label=QLabel("Sampling Rate [s]")
        self.sara_disp=QLCDNumber()
        self.sara=self.query_sara()
        self.sara_disp.display(self.sara)
        trdl_label=QLabel("Trigger Delay [s]")
        self.trdl_disp=QLCDNumber()
        self.trdl=self.query_trdl()
        self.trdl_disp.display(self.trdl)

        self.tdivmenu=QComboBox()
        self.tdivmenu.addItem('1')
        self.tdivmenu.addItem('2')
        self.tdivmenu.addItem('5')
        self.tdivmenu.addItem('10')
        self.tdivmenu.addItem('20')
        self.tdivmenu.addItem('50')
        self.tdivmenu.addItem('100')
        self.tdivmenu.addItem('200')
        self.tdivmenu.addItem('500')

        self.tdivunit=QComboBox()
        self.tdivunit.addItem('ns')
        self.tdivunit.addItem('\u03BCs') # unicode mu
        self.tdivunit.addItem('ms')
        self.tdivunit.addItem('s')

        self.tdivbutton=QPushButton("Set TDiv")
        self.tdivbutton.clicked.connect(self.on_tdivbutton_clicked)

        self.trdledit=QLineEdit()
        self.trdlunit=QComboBox()
        self.trdlunit.addItem('ns')
        self.trdlunit.addItem('\u03BCs')
        self.trdlunit.addItem('ms')
        self.trdlunit.addItem('s')

        self.trdledit.setText('0')

        self.trdlbutton=QPushButton("Set TrDl")
        self.trdlbutton.clicked.connect(self.on_trdlbutton_clicked)

        acq_label=QLabel("Start/Stop Acquisition")
        self.acq_disp=QLabel()
        self.acq_disp.setAlignment(Qt.AlignCenter)
        self.acq_disp.setFrameShape(QFrame.StyledPanel)
        self.acq_button=QPushButton("Toggle Acquisition")
        self.acq_button.clicked.connect(self.toggle_acq)

        try:
            self.wasAcq=self.isAcq()
        except:
            self.wasAcq=True

        if self.wasAcq:
            self.acq_disp.setText("Running")
            self.acq_disp.setStyleSheet("background:limegreen")
        else:
            self.acq_disp.setText("Stopped")
            self.acq_disp.setStyleSheet("background:red")

        self.stats_layout.addWidget(acq_label,0,0,1,2)
        self.stats_layout.addWidget(self.acq_disp,1,0,1,2)
        self.stats_layout.addWidget(self.acq_button,2,0,1,2)
        self.stats_layout.addWidget(sara_label,3,0,1,2)
        self.stats_layout.addWidget(self.sara_disp,4,0,1,2)
        self.stats_layout.addWidget(tdiv_label,5,0,1,2)
        self.stats_layout.addWidget(self.tdiv_disp,6,0,1,2)
        self.stats_layout.addWidget(self.tdivmenu,7,0)
        self.stats_layout.addWidget(self.tdivunit,7,1)
        self.stats_layout.addWidget(self.tdivbutton,8,0,1,2)
        self.stats_layout.addWidget(trdl_label,9,0,1,2)
        self.stats_layout.addWidget(self.trdl_disp,10,0,1,2)
        self.stats_layout.addWidget(self.trdledit,11,0)
        self.stats_layout.addWidget(self.trdlunit,11,1)
        self.stats_layout.addWidget(self.trdlbutton,12,0,1,2)

        self.create_wfsuBox()
        self.stats_layout.addWidget(self.wfsuBox,13,0,1,2)

    def on_tdivbutton_clicked(self):
        try:
            self.set_tdiv(str(self.tdivmenu.currentText()),
                str(self.tdivunit.currentText()))
        except:
            pass

    def on_trdlbutton_clicked(self):
        try:
            self.set_trdl(float(self.trdledit.text()),
                str(self.trdlunit.currentText()))
        except:
            pass

    def create_wfsuBox(self):
        self.wfsuBox=QGroupBox("Waveform Setup")
        self.wfsuLayout=QVBoxLayout()
        self.wfsuBox.setLayout(self.wfsuLayout)

        self.FPedit=QLineEdit()
        self.FPbutton=QPushButton("Set First Point")
        self.FPbutton.clicked.connect(lambda: self.waveformSetup(
            FP=self.FPedit.text()))

        self.NPedit=QLineEdit()
        self.NPbutton=QPushButton("Set Number of Points")
        self.NPbutton.clicked.connect(lambda: self.waveformSetup(
            NP=self.NPedit.text()))

        self.SPedit=QLineEdit()
        self.SPbutton=QPushButton("Set Sparsing")
        self.SPbutton.clicked.connect(lambda: self.waveformSetup(
            SP=self.SPedit.text()))

        self.FPedit.setText('0')
        self.NPedit.setText('all')
        self.SPedit.setText('1')
        self.waveformSetup(FP='0',NP='0',SP='1')

        self.wfsuLayout.addWidget(self.FPedit)
        self.wfsuLayout.addWidget(self.FPbutton)
        self.wfsuLayout.addWidget(self.NPedit)
        self.wfsuLayout.addWidget(self.NPbutton)
        self.wfsuLayout.addWidget(self.SPedit)
        self.wfsuLayout.addWidget(self.SPbutton)

    def create_box1(self):
        self.box1=QGroupBox("Channel 1")
        self.box1layout=QGridLayout()
        self.box1.setLayout(self.box1layout)

        self.create_vdiv1box()
        self.create_ofst1box()

        self.create_chart1()
        self.box1layout.addWidget(self.chart1view,0,0,1,3)

        self.box1layout.addWidget(self.vdiv1box,1,0)
        self.box1layout.addWidget(self.ofst1box,1,1)

        self.save1button=QPushButton("Save Waveform")
        self.save1button.clicked.connect(self.on_save1button_clicked)
        self.box1layout.addWidget(self.save1button,1,2)

    def create_box2(self):
        self.box2=QGroupBox("Channel 2")
        self.box2layout=QGridLayout()
        self.box2.setLayout(self.box2layout)

        self.create_vdiv2box()
        self.create_ofst2box()

        self.create_chart2()
        self.box2layout.addWidget(self.chart2view,0,0,1,3)

        self.box2layout.addWidget(self.vdiv2box,1,0)
        self.box2layout.addWidget(self.ofst2box,1,1)

        self.save2button=QPushButton("Save Waveform")
        self.save2button.clicked.connect(self.on_save2button_clicked)
        self.box2layout.addWidget(self.save2button,1,2)

    def create_vdiv1box(self):
        self.vdiv1box=QGroupBox("Voltage Divison [V]")
        self.vdiv1layout=QGridLayout()
        self.vdiv1box.setLayout(self.vdiv1layout)

        self.vdiv1disp=QLCDNumber()
        try:
            self.vdiv1=self.query_vdiv(1)
        except:
            self.vdiv1=1
        self.vdiv1disp.display(self.vdiv1)

        self.vdiv1menu=QComboBox()
        self.vdiv1menu.addItem('500 \u03BCV')
        self.vdiv1menu.addItem('1 mV')
        self.vdiv1menu.addItem('2 mv')
        self.vdiv1menu.addItem('5 mV')
        self.vdiv1menu.addItem('10 mV')
        self.vdiv1menu.addItem('20 mV')
        self.vdiv1menu.addItem('50 mV')
        self.vdiv1menu.addItem('100 mV')
        self.vdiv1menu.addItem('200 mV')
        self.vdiv1menu.addItem('500 mV')
        self.vdiv1menu.addItem('1 V')
        self.vdiv1menu.addItem('2 V')
        self.vdiv1menu.addItem('5 V')
        self.vdiv1menu.addItem('10 V')

        self.vdiv1button=QPushButton("Set VDiv")
        self.vdiv1button.clicked.connect(self.on_vdiv1button_clicked)

        self.vdiv1layout.addWidget(self.vdiv1disp,0,0,1,2)
        self.vdiv1layout.addWidget(self.vdiv1menu,1,0,1,2)
        self.vdiv1layout.addWidget(self.vdiv1button,2,0,1,2)

    def create_vdiv2box(self):
        self.vdiv2box=QGroupBox("Voltage Divison [V]")
        self.vdiv2layout=QGridLayout()
        self.vdiv2box.setLayout(self.vdiv2layout)

        self.vdiv2disp=QLCDNumber()
        try:
            self.vdiv2=self.query_vdiv(2)
        except:
            self.vdiv2=1
        self.vdiv2disp.display(self.vdiv2)

        self.vdiv2menu=QComboBox()
        self.vdiv2menu.addItem('500 \u03BCV') # unicode mu
        self.vdiv2menu.addItem('1 mV')
        self.vdiv2menu.addItem('2 mv')
        self.vdiv2menu.addItem('5 mV')
        self.vdiv2menu.addItem('10 mV')
        self.vdiv2menu.addItem('20 mV')
        self.vdiv2menu.addItem('50 mV')
        self.vdiv2menu.addItem('100 mV')
        self.vdiv2menu.addItem('200 mV')
        self.vdiv2menu.addItem('500 mV')
        self.vdiv2menu.addItem('1 V')
        self.vdiv2menu.addItem('2 V')
        self.vdiv2menu.addItem('5 V')
        self.vdiv2menu.addItem('10 V')

        self.vdiv2button=QPushButton("Set VDiv")
        self.vdiv2button.clicked.connect(self.on_vdiv2button_clicked)

        self.vdiv2layout.addWidget(self.vdiv2disp,0,0,1,2)
        self.vdiv2layout.addWidget(self.vdiv2menu,1,0,1,2)
        self.vdiv2layout.addWidget(self.vdiv2button,2,0,1,2)

    def on_vdiv1button_clicked(self):
        try:
            self.set_vdiv(1,str(self.vdiv1menu.currentText()))
        except:
            pass

    def on_vdiv2button_clicked(self):
        try:
            self.set_vdiv(2,str(self.vdiv2menu.currentText()))
        except:
            pass

    def create_ofst1box(self):
        self.ofst1box=QGroupBox("Voltage Offset [V]")
        self.ofst1layout=QGridLayout()
        self.ofst1box.setLayout(self.ofst1layout)

        self.ofst1disp=QLCDNumber()
        try:
            self.ofst1=self.query_ofst(1)
        except:
            self.ofst1=0
        self.ofst1disp.display(self.ofst1)
        self.ofst1edit=QLineEdit()

        self.ofst1unit=QComboBox()
        self.ofst1unit.addItem("\u03BCV") # unicode mu
        self.ofst1unit.addItem("mV")
        self.ofst1unit.addItem("V")

        self.ofst1button=QPushButton("Set Offset")
        ofst=self.ofst1edit.text()
        unit=str(self.ofst1unit.currentText())
        self.ofst1button.clicked.connect(self.on_ofst1button_clicked)

        self.ofst1layout.addWidget(self.ofst1disp,0,0,1,2)
        self.ofst1layout.addWidget(self.ofst1edit,1,0)
        self.ofst1layout.addWidget(self.ofst1unit,1,1)
        self.ofst1layout.addWidget(self.ofst1button,2,0,1,2)

    def create_ofst2box(self):
        self.ofst2box=QGroupBox("Voltage Offset [V]")
        self.ofst2layout=QGridLayout()
        self.ofst2box.setLayout(self.ofst2layout)

        self.ofst2disp=QLCDNumber()
        try:
            self.ofst2=self.query_ofst(2)
        except:
            self.ofst2=0
        self.ofst2disp.display(self.ofst2)
        self.ofst2edit=QLineEdit()

        self.ofst2unit=QComboBox()
        self.ofst2unit.addItem("\u03BCV")
        self.ofst2unit.addItem("mV")
        self.ofst2unit.addItem("V")

        self.ofst2button=QPushButton("Set Offset")
        ofst=self.ofst2edit.text()
        unit=str(self.ofst2unit.currentText())
        self.ofst2button.clicked.connect(self.on_ofst2button_clicked)

        self.ofst2layout.addWidget(self.ofst2disp,0,0,1,2)
        self.ofst2layout.addWidget(self.ofst2edit,1,0)
        self.ofst2layout.addWidget(self.ofst2unit,1,1)
        self.ofst2layout.addWidget(self.ofst2button,2,0,1,2)

    def on_ofst1button_clicked(self):
        try:
            self.set_ofst(1,self.ofst1edit.text(),
                str(self.ofst1unit.currentText()))
        except:
            pass

    def on_ofst2button_clicked(self):
        try:
            self.set_ofst(2,self.ofst2edit.text(),
                str(self.ofst2unit.currentText()))
        except:
            pass

    def wf_to_list(self,channel):
        wf=self.getWaveform(channel).pointsVector()
        v=[]
        t=[]
        for i in range(len(wf)):
            point=wf[i]
            t.append(float(point.x()))
            v.append(float(point.y()))
        return t,v

    def on_save1button_clicked(self):
        reps=1000
        t,v=self.wf_to_list(1)
        df=pd.DataFrame(data=[v],columns=t)
        wait(0.001)

        for i in range(reps):
            t,v=self.wf_to_list(1)
            df2=pd.DataFrame(data=[v],columns=t)
            df=df.append(df2,ignore_index=True)
            wait(0.001)

        df=df.transpose()
        wdir='/home/ctalab/data/CTA/testing/waveform/07_28_2021/'
        df.to_csv(wdir+fname+'1.csv')
        print('done')

    def on_save2button_clicked(self):
        reps=1000
        t,v=self.wf_to_list(2)
        df=pd.DataFrame(data=[v],columns=t)
        wait(0.001)

        for i in range(reps):
            t,v=self.wf_to_list(2)
            df2=pd.DataFrame(data=[v],columns=t)
            df=df.append(df2,ignore_index=True)
            wait(0.001)

        df=df.transpose()
        wdir='/home/ctalab/data/CTA/testing/waveform/07_28_2021/'
        df.to_csv(wdir+fname+'2.csv')
        print('done')

    def create_chart1(self):
        self.chart1=QChart()
        try:
            self.series1=self.getWaveform(1)
        except:
            self.series1=QSplineSeries()
        self.chart1.addSeries(self.series1)
        self.chart1.legend().hide()

        self.Xaxis1=QValueAxis()
        self.Xaxis1.setRange(-6*self.tdiv,6*self.tdiv)
        self.Xaxis1.setTickCount(7)
        self.Xaxis1.setLabelFormat('%2.2g')
        self.Xaxis1.setMinorTickCount(1)
        self.chart1.addAxis(self.Xaxis1,Qt.AlignBottom)
        self.series1.attachAxis(self.Xaxis1)

        self.Yaxis1=QValueAxis()
        self.Yaxis1.setRange(-4*self.vdiv1+self.ofst1,4*self.vdiv1+self.ofst1)
        self.Yaxis1.setTickCount(5)
        self.Yaxis1.setLabelFormat('%2.2g')
        self.Yaxis1.setMinorTickCount(1)
        self.chart1.addAxis(self.Yaxis1,Qt.AlignLeft)
        self.series1.attachAxis(self.Yaxis1)

        self.chart1view=QChartView(self.chart1)
        self.chart1.resize(600,400)

    def create_chart2(self):
        self.chart2=QChart()
        try:
            self.series2=self.getWaveform(2)
        except:
            self.series2=QSplineSeries()
        self.chart2.addSeries(self.series2)
        self.chart2.legend().hide()

        self.Xaxis2=QValueAxis()
        self.Xaxis2.setRange(-6*self.tdiv,6*self.tdiv)
        self.Xaxis2.setTickCount(7)
        self.Xaxis2.setMinorTickCount(1)
        self.Xaxis2.setLabelFormat('%2.2g')
        self.chart2.addAxis(self.Xaxis2,Qt.AlignBottom)
        self.series2.attachAxis(self.Xaxis2)

        self.Yaxis2=QValueAxis()
        self.Yaxis2.setRange(-4*self.vdiv2+self.ofst2,4*self.vdiv2+self.ofst2)
        self.Yaxis2.setTickCount(5)
        self.Yaxis2.setMinorTickCount(1)
        self.Yaxis2.setLabelFormat('%2.2g')
        self.chart2.addAxis(self.Yaxis1,Qt.AlignLeft)
        self.series2.attachAxis(self.Yaxis2)

        self.chart2view=QChartView(self.chart2)
        self.chart2.resize(600,400)

    def check_waveform(self):
        try:
            if self.channel1:
                if self.getWaveform(1) != self.series1:
                    self.chart1.removeSeries(self.series1)
                    self.series1=self.getWaveform(1)
                    self.chart1.addSeries(self.series1)
                    self.series1.attachAxis(self.Xaxis1)
                    self.series1.attachAxis(self.Yaxis1)

            if self.channel2:
                if self.getWaveform(2) != self.series2:
                    self.chart2.removeSeries(self.series2)
                    self.series2=self.getWaveform(2)
                    self.chart2.addSeries(self.series2)
                    self.series2.attachAxis(self.Xaxis2)
                    self.series2.attachAxis(self.Yaxis2)
        except:
            pass

    def toggle_acq(self):
        try:
            if self.isAcq():
                self.stopAcq()
            else:
                self.startAcq()
        except:
            pass

    def check_acq(self):
        try:
            if self.wasAcq != self.isAcq():
                self.wasAcq=self.isAcq()
                if self.wasAcq:
                    self.acq_disp.setText("Running")
                    self.acq_disp.setStyleSheet("background:limegreen")
                else:
                    self.acq_disp.setText("Stopped")
                    self.acq_disp.setStyleSheet("background:red")
        except:
            pass

    def check_vdiv(self):
        try:
            if self.channel1:
                if self.vdiv1 != self.query_vdiv(1):
                    self.vdiv1 = self.query_vdiv(1)
                    self.vdiv1disp.display(self.vdiv1)
                    self.Yaxis1.setRange(-4*self.vdiv1+self.ofst1,
                        4*self.vdiv1+self.ofst1)

            if self.channel2:
                if self.vdiv2 != self.query_vdiv(2):
                    self.vdiv2 = self.query_vdiv(2)
                    self.vdiv2disp.display(self.vdiv2)
                    self.Yaxis2.setRange(-4*self.vdiv2+self.ofst2,
                        4*self.vdiv2+self.ofst2)
        except:
            pass

    def check_ofst(self):
        try:
            if self.channel1:
                if self.ofst1 != self.query_ofst(1):
                    self.ofst1 = self.query_ofst(1)
                    self.ofst1disp.display(self.ofst1)
                    self.Yaxis1.setRange(-4*self.vdiv1+self.ofst1,
                        4*self.vdiv1+self.ofst1)

            if self.channel2:
                if self.ofst2 != self.query_ofst(2):
                    self.ofst2 = self.query_ofst(2)
                    self.ofst2disp.display(self.ofst2)
                    self.Yaxis2.setRange(-4*self.vdiv2+self.ofst2,
                        4*self.vdiv2+self.ofst2)
        except:
            pass

    def check_tdiv(self):
        try:
            if self.tdiv != self.query_tdiv():
                self.tdiv = self.query_tdiv()
                self.tdiv_disp.display(self.tdiv)
                if self.channel1:
                    self.Xaxis1.setRange(-6*self.tdiv,6*self.tdiv)
                    self.series1.attachAxis(self.Xaxis1)
                if self.channel2:
                    self.Xaxis2.setRange(-6*self.tdiv,6*self.tdiv)
                    self.series2.attachAxis(self.Xaxis2)
        except:
            pass

    def check_sara(self):
        try:
            if self.sara != self.query_sara():
                self.sara = self.query_sara()
                self.sara_disp.display(self.sara)
        except:
            pass

    def check_trdl(self):
        try:
            if self.trdl != self.query_trdl():
                self.trdl=self.query_trdl()
                self.trdl_disp.display(self.trdl)
        except:
            pass

    ## reading/writing functions
    def open_siglent(self, path, wait=None):
        rm=visa.ResourceManager()
        self.Siglent=rm.open_resource(path)

        self.Siglent.write("CHDR OFF") # format responses
        self.Siglent.timeout=30000 # 30 seconds, default is 2, not long enough
        self.Siglent.chunk_size=20*1024**2 # 20 MB, default is 20 KB, too small

        try:
            if self.Siglent.query("MSIZ?") != "14M\n":
                self.Siglent.write("MSIZ 14M")
        except:
            pass

        if wait is None:
            wait=self.wait

        sleep(wait)

    def query_ofst(self,channel):
        ret=self.Siglent.query(("C{}:OFST?").format(channel))
        return float(ret)

    def query_vdiv(self,channel):
        ret=self.Siglent.query(("C{}:VDIV?").format(channel))
        return float(ret)

    def query_tdiv(self):
        ret=self.Siglent.query("TDIV?")
        return float(ret)

    def query_sara(self):
        ret=self.Siglent.query("SARA?")
        return float(ret)

    def query_trdl(self):
        ret=self.Siglent.query("TRDL?")
        return float(ret)

    def set_vdiv(self,channel,vdiv,wait=None):
        # possible VDIV:
        # 500 UV (micro)
        # 1,2,5,10,20,50,100,200,500 MV
        # 1,2,5,10 V
        if vdiv=="500 \u03BCV":
            vdiv="500UV" # change unicode mu to letter u
        vdiv.replace(' ','') # get rid of space in '10 mV'
        vdiv=vdiv.upper() # set unit uppercase
        self.Siglent.write(("C{}:VDIV {}").format(channel,vdiv))
        if wait is None:
            wait=self.wait
        sleep(wait)

    def set_ofst(self,channel,ofst,unit,wait=None):
        # can be anything in UV/MV/V ?
        if unit=="\u03BCV":
            unit="UV" # change unicode mu to letter u
        unit=unit.upper() # set unit uppercase
        self.Siglent.write(("C{}:OFST {}{}").format(channel,ofst,unit))
        if wait is None:
            wait=self.wait
        sleep(wait)

    def set_tdiv(self,tdiv,unit,wait=None):
        # possible TDIV:
        # 1,2,5,10,20,50,100,200,500 NS
        # 1,2,5,10,20,50,100,200,500 US (micro)
        # 1,2,5,10,20,50,100,200,500 MS
        # 1,2,5,10,20,50,100 S
        if unit=="\u03BCs":
            unit="US" # change unicode mu to letter u
        elif (unit=='s') and ((tdiv=='200') or (tdiv=='500')):
            tdiv='100' # can't set tdiv to 200 or 500 S, so set to max (100 S)
        unit=unit.upper() # set unit uppercase
        self.Siglent.write(("TDIV {}{}").format(tdiv,unit))
        if wait is None:
            wait=self.wait
        sleep(wait)

    def set_trdl(self,trdl,unit,wait=None):
        if unit=='ns':
            mult=10**-9
        elif unit=='\u03BCs':
            mult=10**-6
            unit="US"
        elif unit=='ms':
            mult=10**-3
        else:
            mult=1

        if (trdl*mult)<=(self.tdiv*10):
            unit=unit.upper()
            self.Siglent.write(("TRDL {}{}").format(trdl,unit))
            if wait is None:
                wait=self.wait
            sleep(wait)

    def getWaveform(self,channel):
        self.Siglent.write(("C{}:WF? DAT2").format(channel))
        ret=list(self.Siglent.read_raw())[15:]
        ret.pop() # remove last two items (message end bits)
        ret.pop()
        ret.pop(0)
        vdiv=self.query_vdiv(channel)
        ofst=self.query_ofst(channel)

        vlist=[]

        for v in ret:
            if v>127:
                v=v-255
            v=(v/25*vdiv-ofst)
            vlist.append(v)

        points=QSplineSeries()

        tdiv=self.tdiv
        sara=self.sara

        for i in range(len(vlist)):
            t=-tdiv*7+i/sara
            points.append(t,vlist[i])

        return points


    def waveformSetup(self, FP=None, NP=None, SP=None, wait=None):
        #FP: First point
        # address of first data point to be sent
        # index starts at 0
        #NP: Number of points
        # how many points should be transmitted
        # 0: send all
        # 1: send 1
        # 500: send <= 500
        #SP: Sparsing
        # interval between data points
        # 0: send all
        # 1: send all
        # 2: send every other
        # 5: send every 5th

        if FP is None:
            FP=self.querySetup()[0]
        if NP is None:
            NP=self.querySetup()[1]
        elif NP.lower()=='all':
            NP='0'
        if SP is None:
            SP=self.querySetup()[2]

        self.Siglent.write(("WFSU? FP,{},NP,{},SP,{}").format(FP,NP,SP))
        # default: FP=0,NP=1000,SP=4
        if wait is None:
            wait=self.wait
        sleep(wait)

    def querySetup(self):
        ret=self.Siglent.query("WFSU?")
        ret=ret.strip("'")
        lst=ret.split(',')
        return [float(lst[1]),float(lst[3]),float(lst[5])]
        # format: [FP,NP,SP]

    def startAcq(self,wait=None):
        self.Siglent.write("TRMD AUTO")
        if wait is None:
            wait=self.wait
        sleep(wait)

    def stopAcq(self,wait=None):
        self.Siglent.write("STOP")
        if wait is None:
            wait=self.wait
        sleep(wait)

    def isAcq(self):
        ret=self.Siglent.query("TRMD?")
        if ret=="STOP\n":
            return False
        else:
            return True

    def closeEvent(self,event):
        self.Siglent.close()
        event.accept()

    def wf_to_array(self,channel):
        wf=self.getWaveform(channel).pointsVector()
        for i in range(len(wf)):
            point=wf[i]
            wf[i]=[float(point.x()),float(point.y())]
        wf=np.array(wf)
        print(wf)
        return wf


if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyle('Fusion')
    wg=WidgetGallery()
    wg.show()
    sys.exit(app.exec_())
