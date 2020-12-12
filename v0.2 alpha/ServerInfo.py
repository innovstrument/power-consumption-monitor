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
const.PATH = r'.\ipmish -ip '

class Status(enum.Enum):
    ON = "ON"
    OFF = "OFF"
    PROCESSING = "PROCESSING"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"

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
        self._priority = 0

    def getInfo(self)->list:
        return [self._ipAddr, self._userName, self._password, round(self._power, 2), self._status.value, self._lastUpd]
    def getPower(self):
        lock.acquire()
        self._status = Status.PROCESSING        
        cmd = const.PATH + self._ipAddr + ' -u '+ self._userName + ' -p ' + self._password + ' sensor numeric -format legacy'   
        #print(cmd)     
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,encoding="utf-8")
        out = p.communicate()        
        if p.returncode != 0:
            lock.release()            
            return p.returncode
        lock.release()
        s = out[0].__str__()
        s = s.replace(' ','')
        print(s)
        s = s.split('\n')
        voltage = 0
        amp = 0.0
        lock.acquire()
        for i in s:
            i = i.split('|')
            if i[-1]=='Volts':
                v = float(i[-2])
                voltage = max(voltage,v)
                self._minVoltage = min(self._minVoltage,v)
            elif i[-1]=='Amps':
                a = float(i[-2])
                amp += a
            elif i[-1] == 'Watts':
                p= float(i[-2])
                if p==0:
                    self._power = 0
                    self._status = Status.OFF
                    self._minVoltage = sys.maxsize
                    lock.release()
                    return 0
                elif p > 0 and voltage == 0:
                    self._status = Status.PROCESSING
                    lock.release()
                    return 0


        power = voltage * amp
        print(power)
        if(power > 0):
           
            self._status = Status.ON
        elif (power == 0):
            self._status = Status.OFF
        self._power = power
        #print(power)
        self._lastUpd = self.timeStamp()
        lock.release()
        return 0

    def powerCmd(self, cmd:str):
        cmd = const.PATH + self._ipAddr + r' -u '+ self._userName + r' -p ' + self._password + r' power ' + cmd
        print(cmd)
        print(lock.acquire())
        #lock.acquire()
        print('a')
        if cmd == 'off':
            self._power = 0
            self._minVoltage = sys.maxsize
            self._status = Status.OFF
        else:
            
            self._status = Status.PROCESSING
        self._lastUpd = self.timeStamp()
        lock.release()
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,encoding="utf-8") 
        #p.communicate()      
        #print(p.returncode)
    
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

    def timeOut(self):
        lock.acquire()
        self._status = Status.TIMEOUT
        self._lastUpd = self.timeStamp()
        lock.release()

    @property
    def minVoltage(self):
        return self._minVoltage
    @property
    def priority(self):
        return self._priority
    @priority.setter
    def priority(self, priority):
        lock.acquire()
        self._priority += priority
        lock.release()
