import visa 
import pylab as pl
import datetime
import numpy as np

rm=visa.ResourceManager()
inst=rm.open_resource('USB0::62701::60986::SDS1ECDD2R8216::0::INSTR')
inst.write("CHDR OFF")


def wf():
    vdiv=inst.query("C1:VDIV?")
    ofst=inst.query("C1:OFST?")
    tdiv=inst.query("TDIV?")
    sara=inst.query("SARA?")

    inst.write("WFSU FP,0,NP,1000,SP,1")

    inst.timeout=30000
    inst.chunk_size=20*1024**2
    inst.write("C1:WF? DAT2")
    ret=list(inst.read_raw())[16:]
    ret.pop()
    ret.pop()

    volts=[]
    for n in ret:
        if n>127:
            n=n-255
        volts.append(n)
    times=[]
    for i in range(len(volts)):
        volts[i]=volts[i]/25*float(vdiv)-float(ofst)
        t=-(float(tdiv)*7)+(i/float(sara))
        times.append(t)

    return times,volts
 

def plot_data(x,y):

    pl.figure(figsize=(7,5))
    pl.plot(x,y,marker='o',markersize=2)
    pl.legend()
    pl.grid()
    pl.show()

def data_to_array():
    t,v=wf()
    array=np.array([t,v]).transpose()
    return array

print(data_to_array())
