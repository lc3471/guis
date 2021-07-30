README

Laurel Carpenter
07/30/2021

Instructions for use of GUIs and explanation of their development

general notes:
-all GUI classes contain super clauses because I was going to use them and then
 I didn't, and I forgot to remove them. sorry!
-all GUIs are available as individual programs and as modules that can be
imported into master_gui. master_gui is currently configured to display the
pulser, both PSUs, and the motion controller on the ctalab desktop monitor at
Nevis. if you want to run all GUIs at the same time, run master_gui AND
scope_gui.
-all GUIs contain a closeEvent function that will disconnect the instrument
when the GUI window is closed. PSUs and pulser also turn off outputs upon a
close event, and motion controller turns off motors (scope turns off nothing,
as it performs acquisition rather than output, but can be modified so that
acquisition turns off upon a close event).

basic GUI design:
The most basic GUI here is the single PSU, which contains only QLabels,
QLCDNumbers, QPushButtons, and QLineEdits. There are two basic setups: a
toggle setup (made up of a QLabel display and a QPushButton) and a number
readout (made up of a QLCDNumber display and possibly a QLabel, and a
QPushButton).
The toggle setup displays a red box when the value is off/False and a green
(color code 'limegreen') box when the value is on/True. The value is toggled
by clicking the QPushButton.
The number setup displays a value as a QLCDNumber (and possibly an additional
QLabel displaying the 'set'/'desired' value as opposed to the actual readout),
followed by a QLineEdit where the user can input any value they want, and a
QPushButton to set that value.
-single PSU is made up of one toggle setup for output, and two number setups for
 voltage and current.
-double PSU essentially has what the single PSU has twice, plus an additional
toggle setup for voltage tracking and a toggle button for master (i.e. both)
outputs.
-pulser has toggle setups for using each channel, output, polarity, sync, sync
polarity, and holding width/duty cycle, and number setups for duty cycle, pulse
delay, pulse width, transition leading, and transition trailing. frequency,
amplitude, offset, and delay are also number displays, but they are controlled
by a single push button (due to the way in which the instrument reads commands).
 Impedance is controlled by a toggle button, but the display is handled by a
QLCDNumber as opposed to a QLabel.
-scope uses a toggle setup for acquisition and a number setup for the waveform
setup controls, and a QLCDNumber for sampling rate (no buttons bc this cannot be
 changed). vdiv, offset, tdiv, and trigger delay are all handled by a QComboBox,
 a QLineEdit, and  QPushButton. A QComboBox is a drop-down menu so the user can
choose which units to use and specific values for vdiv and tdiv. The scope also
uses the QChart package for displaying the waveform. Data points are added to a
QSplineSeries (similar to a QLineSeries, but with smoothing) and displayed on
the chart.
-motion controller uses a combination of toggle setups, number setups, QComboBox
 and QLineEdit setups for user input, and individual QPushButtons for motion.

 I will include notes on troubleshooting and individual specifications in each
 program. 
