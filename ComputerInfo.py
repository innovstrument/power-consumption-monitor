import os
import subprocess
import re
import tkinter
import sys
import csv
from tkinter import ttk
import threading
import enum
import time

lock = threading.Lock()

class _const(object):
    class ConstError(PermissionError):pass
    def __setattr__(self, name, value):
        if name in self.__dict__.keys():
            raise self.ConstError("Can't rebind const(%s)" % name)
        self.__dict__[name]=value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise  self.ConstError("Can't unbind const(%s)" % name)
        raise  NameError(name)
const = _const()
const.PATH = r'ipmish.exe -ip '

class Status(enum.Enum):
    ON = "ON"
    OFF = "OFF"
    PROCESSING = "PROCESSING"
    TIMEOUT = "TIMEOUT"

class Computer:
    @staticmethod
    def timeStamp() ->str:
        now = int(round(time.time()*1000))
        now02 = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(now/1000))
        return now02

    def __init__(self, ipAddr, userName, password, power = 0, minVoltage = sys.maxsize, status = Status.PROCESSING):
        self._ipAddr = ipAddr
        self._userName = userName
        self._password = password
        self._power = power
        self._minVoltage = minVoltage
        self._status = status
        self._lastUpd = self.timeStamp()

    def getInfo(self)->list:
        return [self._ipAddr, self._userName, self._password, round(self._power, 2), self._status.value, self._lastUpd]
    def getPower(self) -> int:
        lock.acquire()
        self._status = Status.PROCESSING
        lock.release()
        cmd = const.PATH + self._ipAddr + ' -u '+ self._userName + ' -p ' + self._password + ' sensor numeric'        
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,encoding="utf-8")
        out = p.communicate()
        #print(out[0])
        s = out[0].__str__()
        s.replace('\t','')
        ss = s.split('\n')
        voltage = 0
        amp = 0.0
        lock.acquire()
        for i in ss:
            if i=='':
                continue
            sss = i.split(': ',)
            #print(sss)
            if sss[1].endswith('V'):
                pattern = re.compile(r'\d+')
                v = int(re.findall(pattern,sss[1])[0])
                voltage = max(voltage,v)
                self._minVoltage = min(self._minVoltage,v)
                #print(v)
            if sss[1].endswith('AMP'):
                pattern = re.compile(r'(\d+(\.\d+)?)')
                print(re.findall(pattern,sss[1])[0])
                a = float(re.findall(pattern,sss[1])[0][0])
                amp += a
                #print(a)
            if sss[1].endswith('Watts') and sss[0].startswith('Reading'):
                pattern = re.compile(r'(\d+(\.\d+)?)')
                p = float(re.findall(pattern,sss[1])[0][0])
                if p==0:
                    return 0

        power = voltage * amp
        if(power > 0):
            self._status = Status.ON
        self._power = power
        #print(power)
        self._lastUpd = self.timeStamp()
        lock.release()
        return power

    def powerCmd(self, cmd:str):
        cmd = const.PATH + self._ipAddr + r' -u '+ self._userName + r' -p ' + self._password + r' power ' + cmd
        lock.acquire()
        if cmd == 'off':
            self._power = 0
            self._status = Status.OFF
        else:
            self._status = Status.PROCESSING
        self._lastUpd = self.timeStamp()
        lock.release()
        subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,encoding="utf-8")       

    
    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, power):
        lock.acquire()
        self._power = power
        self._lastUpd = self.timeStamp()
        lock.release()

    @property
    def ip(self):
        return self._ipAddr

    @ip.setter
    def ip(self, ip):
        lock.acquire()
        self._ipAddr = ip
        self._lastUpd = self.timeStamp()
        lock.release()

    @property
    def status(self):
        return self._status

    #@status.setter
    def timeOut(self):
        lock.acquire()
        self._status = Status.TIMEOUT
        self._lastUpd = self.timeStamp()
        lock.release()

    @property
    def minVoltage(self):
        return self._minVoltage
