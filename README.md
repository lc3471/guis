Laurel Carpenter
07/30/2021

Instructions for use of GUIs and explanation of their development

general note:
-all GUIs are available as individual programs and as modules that can be
imported into master_gui. master_gui is currently configured to display the
pulser, both PSUs, and the motion controller on the ctalab desktop monitor at
Nevis. if you want to run all GUIs at the same time, run master_gui AND
scope_gui.

basic class setup:
-each GUI begins with a WidgetGallery class which inherits from QDialog, opens
the instrument as an object of the corresponding instrument class, starts a
timer, sets the main layout, and calls one or more functions to create
additional boxes inside the WidgetGallery.
-a function that creates a box (usually named 'create_{name}box') will create
and set the box's layout, and creates any widgets in the box and/or calls
functions to create additional boxes, and adds those widgets and/or boxes to the
 box's layout.
-whenever the timer runs out it will call a check function (usually named
'check_{name}') which queries the machine and checks if a certain value is
different from the previously stored value. if so, the widget(s) displaying
this value are changed.
-whenever a button is clicked that is meant for toggling (i.e. the parameter has
 two possible values, i.e. can be represented by a boolean), a function will be
called (usually named 'toggle_{name}') that queries the machine:
  if parameter is True:
    write to machine to set False
  else: (i.e. parameter is False):
    write to machine to set True
-whenever a button is clicked for a parameter that cannot be represented as a
bool (i.e. can be more than two values: value can be selected from a drop-down
list or inputted by user), a function is called (usually named
'on_{name}button_clicked') that accesses the current text of the correct widget
(current selection if widget is a menu, user input if widget is a text edit) and
 writes to the machine to set the corresponding parameter to that value.
-finally, each class contains a closeEvent function which turns off the
instrument's motors/outputs/etc and closes communication with the instrument
when a closeEvent is triggered (i.e. the GUI window is closed).

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
