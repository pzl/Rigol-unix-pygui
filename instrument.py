import os
import sys
 
class OScopeError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class usbtmc:
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""
 
    def __init__(self, device):
        self.device = device
        try:
            self.FILE = os.open(device, os.O_RDWR)
        except OSError as e:
            raise OScopeError("Error opening device: "+str(e))
 
 
    def write(self, command):
        try:
            os.write(self.FILE, command)
        except OSError as e:
            print >> sys.stderr, "Write Error: ", e
 
    def read(self, length = 300):
        try:
            return os.read(self.FILE, length)
        except OSError as e:
            if e.args[0] == 110:
                print >> sys.stderr, "Read Error: Read timeout"
            else:
                print >> sys.stderr, "Read Error: ", e
            return ""
 
    def getName(self):
        self.write("*IDN?")
        return self.read(300)
 
    def sendReset(self):
        self.write("*RST")

    def close(self):
        os.close(self.FILE)
 
 
class RigolScope:
    """Class to control a Rigol DS1000 series oscilloscope"""
    def __init__(self, device):
        self.meas = usbtmc(device)
 
        self.name = self.meas.getName()
 
        print self.name
 
    def write(self, command):
        """Send an arbitrary command directly to the scope"""
        self.meas.write(command)
 
    def read(self, command):
        """Read an arbitrary amount of data directly from the scope"""
        return self.meas.read(command)
 
    def reset(self):
        """Reset the instrument"""
        self.meas.sendReset()

    def close(self):
        self.meas.close()