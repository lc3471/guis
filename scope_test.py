import visa 
import pylab as pl
import datetime
import numpy as np
import pandas as pd


rm=visa.ResourceManager()
inst=rm.open_resource('USB0::62701::60986::SDS1ECDD2R8216::0::INSTR')
inst.write("CHDR OFF")

vdiv=inst.query("C1:VDIV?")
ofst=inst.query("C1:OFST?")
tdiv=inst.query("TDIV?")
sara=inst.query("SARA?")

inst.write("WFSU FP,0,NP,1000,SP,1")

inst.timeout=30000
inst.chunk_size=20*1024**2

def wf():
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

#f=open('/media/ctalab/DATA/CTA/testing/waveform/07_27_2021/test500.txt','a')

t,v=wf()
df=pd.DataFrame(data=[v],columns=t)



for n in range(500):
    t,v=wf()
    df2=pd.DataFrame(data=[v],columns=t)
    df=df.append(df2,ignore_index=True)

df=df.transpose()

wdir = "/home/ctalab/data/CTA/testing/waveform/07_27_2021/"
df.to_csv(wdir+"35_5.csv")

#f.close()

