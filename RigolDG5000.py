#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# Copyright (c) 2018, Stephen Goadhouse <sgoadhouse@virginia.edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
 
#-------------------------------------------------------------------------------
#  Control a Aim TTi PL-P Series DC Power Supplies with PyVISA
#-------------------------------------------------------------------------------

# For future Python3 compatibility:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

try:
    from . import SCPI
except ValueError:
    from SCPI import SCPI
    
from time import sleep
import pyvisa as visa
import re

def xstr(s):
    return str(s or '')

class RigolDG5000(SCPI):
    """Basic class for controlling and accessing an Aim TTi EL302P-USB
    Power Supply. This series of power supplies only minimally adheres
    to any LXI specifications and so it uses its own commands although
    it adheres to the basic syntax of SCPI. The underlying accessor
    functions of SCPI.py are used but the top level are all re-written
    below to handle the very different command syntax. This shows how
    one might add packages to support other such power supplies that
    only minimally adhere to the command standards.
    """

    def __init__(self, resource, wait=1.0):
        """Init the class with the instruments resource string

        resource - resource string or VISA descriptor, like TCPIP0::192.168.1.100::9221::SOCKET 
        wait     - float that gives the default number of seconds to wait after sending each command

        NOTE: According to the documentation for this power supply, the
        resource string when using the Ethernet access method must look
        like TCPIP0::192.168.1.100::9221::SOCKET where 192.168.1.100 is
        replaced with the specific IP address of the power supply. The
        inclusion of the 9221 port number and SOCKET keyword are
        apparently mandatory for these power supplies.
        """
        super(RigolDG5000, self).__init__(resource, max_chan=3, wait=wait,
                cmd_prefix='',
                read_termination='',
                write_termination='\r\n')
        self.open()

    def beeperOn(self):
        """Enable the system beeper for the instrument"""
        # NOTE: Unsupported command by this power supply. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass
        
    def beeperOff(self):
        """Disable the system beeper for the instrument"""
        # NOTE: Unsupported command by this power supply. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass
        
    def isOutputOn(self, channel=None):
        """Return true if the output of channel is ON, else false
        """
            
        _str = (':OUTP{}?').format(channel)
        ret = self._instQuery(_str)
        
        if (ret=="ON\n\n"):
            return True
        else:
            return False
    
    def outputOn(self, channel=None, wait=None):
        """Turn on the output for channel
        
           wait    - number of seconds to wait after sending command
        """
            
        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait
            
        str_ = (':OUTP{}:STAT ON').format(channel)
        self._instWrite(str_)
        sleep(wait)             # give some time for PS to respond
    
    def outputOff(self, channel=None, wait=None):
        """Turn off the output for channel
        """
                    
        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait
            
        str_ = (':OUTP{}:STAT OFF').format(channel)
        self._instWrite(str_)
        sleep(wait)             # give some time for PS to respond


    # pulse
    def applyPulse(self, freq=1000, amp=5, offset=None, delay=None, channel=None, wait=None):
        # freq: unit=Hz, 1 micro-Hz to 50 MHz
        # amp: unit=Vpp
        # offset: unit=Vdc
        # delay: unit=s

        if wait is None:
            wait=self._wait

        str_=(":SOUR{}:APPL:PULS {},{},{},{}").format(channel,freq,amp,offset,delay)
        self._instWrite(str_)
        sleep(wait)
    
    def queryApply(self, channel=None, wait=None):

        if wait is None:
            wait=self._wait
        
        str_=(":SOUR{}:APPL?").format(channel)
        ret=self._instQuery(str_)
        ret=ret[:(len(ret)-2)] # remove '\n' from end of string
        ret=ret.strip('"') # remove quotes from beginning and end of string
        lst=ret.split(",") # split string into variables
        
        for i in range(1,len(lst)):
            if lst[i]=="DEF":
                lst[i]=0
            else:
                lst[i]=float(lst[i])
        # lst='waveform name', 'freq', 'amp', 'offset', 'phase/delay'

        return lst

    def dutyCycle(self, pct=None, channel=None, wait=None, Min=False, Max=False):

        if wait is None: 
            wait=self._wait

        if Min:
            str_=(":SOUR{}:PULS:DCYC MIN").format(channel)
        elif Max:
            str_=(":SOUR{}:PULS:DCYC MAX").format(channel)
        else:
            str_=(":SOUR{}:PULS:DCYC {}").format(channel, pct)
        
        self._instWrite(str_)
        sleep(wait)

    def queryDutyCycle(self, channel=None, wait=None):

        if wait is None:
            wait=self._wait

        str_=(":SOUR{}:PULS:DCYC?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)

        return ret

    def pulseDelay(self, delay=None, channel=None, wait=None, Min=False, Max=False):

        if wait is None:
            wait=self._wait

        if Min:
            str_=(":SOUR{}:PULS:DEL MIN").format(channel)
        elif Max:
            str_=(":SOUR{}:PULS:DEL MAX").format(channel)
        else:
            str_=(":SOUR{}:PULS:DEL {}").format(channel, delay)

        self._instWrite(str_)
        sleep(wait)

    def queryDelay(self, channel=None, wait=None):

        if wait is None:
            wait=self._wait

        str_=(":SOUR{}:PULS:DEL?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)

        return ret

    def holdWidth(self, channel=None, wait=None):

        if wait is None:
            wait=self._wait
        
        str_=(":SOUR{}:PULS:HOLD WIDT").format(channel)
        self._instWrite(str_)
        sleep(wait)

    def holdDuty(self, channel=None, wait=None):

        if wait is None:
            wait=self._wait

        str_=(":SOUR{}:PULS:HOLD DUTY").format(channel)
        self._instWrite(str_)
        sleep(wait)

    def isWidth(self, channel=None, wait=None):
        #if not WIDT, DUTY

        if wait is None:
            wait=self._wait

        str_=(":SOUR{}PULS:HOLD?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        
        if ret=="WIDT":
            return True
        else:
            return False

    def transitionLeading(self, seconds=None, channel=None, wait=None, Min=False, Max=False):

        if wait is None:
            wait=self._wait

        if Min:
            str_=(":SOUR{}:PULS:TRAN MIN").format(channel)
        elif Max:
            str_=(":SOUR{}:PULS:TRAN MAX").format(channel)
        else:
            str_=("SOUR{}:PULS:TRAN {}").format(channel, seconds)

        self._instWrite(str_)
        sleep(wait)

    def queryTransLead(self, channel=None, wait=None):

        if wait is None:
            wait=self._wait

        str_=(":SOUR{}:PULS:TRAN?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)

        return ret

    def transitionTrailing(self, seconds=None, channel=None, wait=None, Min=False, Max=False):

        if wait is None:
            wait=self._wait

        if Min:
            str_=(":SOUR{}:PULS:TRAN:TRA MIN").format(channel)
        elif Max:
            str_=(":SOUR{}:PULS:TRAN:TRA MAX").format(channel)
        else:
            str_=("SOUR{}:PULS:TRAN:TRA {}").format(channel, seconds)

        self._instWrite(str_)
        sleep(wait)

    def queryTransTrail(self, channel=None, wait=None):

        if wait is None:
            wait=self._wait

        str_=(":SOUR{}:PULS:TRAN:TRA?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)

        return ret

    def pulseWidth(self, seconds=None, channel=None, wait=None, Min=False, Max=False):

        if wait is None:
            wait=self._wait

        if Min:
            str_=(":SOUR{}:PULS:WIDT MIN").format(channel)
        elif Max:
            str_=(":SOUR{}:PULS:WIDT MAX").format(channel)
        else:
            str_=("SOUR{}:PULS:WIDT {}").format(channel, seconds)

        self._instWrite(str_)
        sleep(wait)

    def queryWidth(self, channel=None, wait=None):

        if wait is None:
            wait=self._wait

        str_=(":SOUR{}:PULS:WIDT?").format(channel)
        ret=self._instQuery(str_)
        ret=ret.strip('"')
        ret=float(ret)

        return ret

    def setImpedance(self, ohms=None, channel=None, wait=None, inf=False, Min=False, Max=False):

        if wait is None:
            wait=self._wait

        if inf:
            str_=(":OUTP{}:IMP INF").format(channel)
        

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Access and control a Aim TTi PL-P Series power supply')
    parser.add_argument('chan', nargs='?', type=int, help='Channel to access/control (starts at 1)', default=1)
    args = parser.parse_args()

    from time import sleep
    from os import environ
    resource = environ.get('TTIPLP_IP', 'TCPIP0::192.168.1.100::9221::SOCKET')
    ttiplp = AimTTiPLP(resource)
    ttiplp.open()

    ## set Remote Lock On
    #ttiplp.setRemoteLock()
    
    ttiplp.beeperOff()
    
    if not ttiplp.isOutputOn(args.chan):
        ttiplp.outputOn()
        
    print('Ch. {} Settings: {:6.4f} V  {:6.4f} A'.
              format(args.chan, ttiplp.queryVoltage(),
                         ttiplp.queryCurrent()))

    voltageSave = ttiplp.queryVoltage()
    
    #print(ttiplp.idn())
    print('{:6.4f} V'.format(ttiplp.measureVoltage()))
    print('{:6.4f} A'.format(ttiplp.measureCurrent()))

    ttiplp.setVoltage(2.7)

    print('{:6.4f} V'.format(ttiplp.measureVoltage()))
    print('{:6.4f} A'.format(ttiplp.measureCurrent()))

    ttiplp.setVoltage(2.3)

    print('{:6.4f} V'.format(ttiplp.measureVoltage()))
    print('{:6.4f} A'.format(ttiplp.measureCurrent()))

    ttiplp.setVoltage(voltageSave)

    print('{:6.4f} V'.format(ttiplp.measureVoltage()))
    print('{:6.4f} A'.format(ttiplp.measureCurrent()))

    ## turn off the channel
    ttiplp.outputOff()

    ttiplp.beeperOn()

    ## return to LOCAL mode
    ttiplp.setLocal()
    
    ttiplp.close()
