#!/usr/bin/python

import numpy
import instrument

scope = instrument.RigolScope("/dev/usbtmc0")
#scope.write(":beep:act")
#scope.write(":beep:act")
scope.write(":stop")

scope.write(":wav:pin:mode nor")

scope.write(":wav:data? chan1")
rawdata = scope.read(100)
data = 255 - numpy.frombuffer(rawdata, 'B', offset=10)


scope.write(":chan1:scal?")
vscale = float(scope.read(20)) #in volts
scope.write(":chan1:offs?")
voff = float(scope.read(20)) #in volts


scope.write(":tim:scal?")
tscale = float(scope.read(20)) #in seconds
scope.write(":tim:offs?")
toff = float(scope.read(20)) #in seconds


time = numpy.arange(-300./50*tscale, 300./50*tscale, tscale/50)
data = (data - 130.0 - voff/vscale*25) / 25*vscale

if time[-1:] < 1e-3:
	time *= 1e6
	tUnit = "uS"
elif time[-1:] < 1:
	time *= 1e3
	tUnit = "mS"
else:
	tUnit = "S"

time = numpy.resize(time,(1,data.size))
print tUnit
print numpy.vstack((data,time)).T

scope.write(":key:lock dis")
scope.close()