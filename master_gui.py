# Laurel Carpenter 
# 07/28/2021

from psu1 import PSU1
from psu2 import PSU2
from pulse import Pulse
from scope import Scope
from motion import Motion

from PyQt5.QtChart import QChartView, QChart, QLineSeries, QSplineSeries, QValueAxis
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLCDNumber,
        QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QMessageBox)

import sys

class WidgetGallery(QDialog):
    def __init__(self,parent=None):
        super(WidgetGallery,self).__init__(parent)

        mainLayout=QGridLayout()

        self.PSU1=PSU1()
        self.PSU2=PSU2()
        self.Pulse=Pulse()
        #self.Scope=Scope()
        self.Motion=Motion()
        

        mainLayout.addWidget(self.PSU1,0,1)
        mainLayout.addWidget(self.PSU2,1,1)
        mainLayout.addWidget(self.Pulse,0,0,3,1)
        #mainLayout.addWidget(self.Scope,0,1)
        mainLayout.addWidget(self.Motion,2,1)

        self.Pulse.setMaximumSize(1100,1000)
        self.PSU1.setMaximumSize(700,1000)
        self.PSU2.setMaximumSize(700,1000)
        self.Motion.setMaximumSize(700,1000)
        self.setLayout(mainLayout)

    def closeEvent(self,event):
        if self.PSU1.isConnected:
            self.PSU1.aim1.outputOff(wait=0)
            self.PSU1.aim1.close()
        if self.PSU2.isConnected:
            self.PSU2.aim2.outputOffAll(wait=0)
            self.PSU2.aim2.close()
        if self.Pulse.isConnected:
            self.Pulse.Rigol.outputOff(1,wait=0)
            self.Pulse.Rigol.outputOff(2,wait=0)
            self.Pulse.Rigol.close()
        """if self.Scope.isConnected:
            self.Scope.Siglent.close_inst()"""
        if self.Motion.isConnected:
            self.Motion.newport.motor_off(1)
            self.Motion.newport.motor_off(2)
            self.Motion.newport.close_inst()
        event.accept()


if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyle('Fusion')
    wg=WidgetGallery()
    wg.show()
    sys.exit(app.exec_())

