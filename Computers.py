import os
import subprocess
import re
import tkinter
import sys
import csv
from tkinter import ttk
import ComputerInfo

class ComputerMngt:
    #key = selection, value = computer
    compList = {}
    #itemList = {}
    def __init__(self):
        self._count = 0
    def add(self, c:ComputerInfo.Computer, selection:str):
        ComputerMngt.compList[selection] = c        
        self._count += 1

    def getComputer(self,selection:str) -> ComputerInfo:
        return ComputerMngt.compList.get(selection)

    def setComputer(self,selection:str, c:ComputerInfo.Computer ) -> ComputerInfo:
        ComputerMngt.compList[selection] = c  

    def getTotalPower(self)->float:
        totalP = 0.0
        for item in ComputerMngt.compList.values():
            totalP+=item.power
        return totalP

    def getMinVoltage(self)->int:
        minV = sys.maxsize
        for item in ComputerMngt.compList.values():
            minV = min(minV,item.minVoltage)
        return minV
    
    def removeComputer(self,selection:str):
        ComputerMngt.compList.pop(selection)
    
    def managePower(self, maxCurrent):
        maxPower = maxCurrent*self.getMinVoltage()
        totalPower = self.getTotalPower()
        if maxPower *0.8 <= totalPower:             
            power = {}
            for k,v in ComputerMngt.compList:
                if v.status != ComputerInfo.Status.OFF and v.status != ComputerInfo.Status.TIMEOUT and v.power > 0:
                    power[v.power] = k                 
            count = 0
            power = list(power)
            while(maxPower *0.8 <= totalPower):
                c = ComputerMngt.compList[power[count][1]]
                totalPower -= c.power
                count += 1
                c.powerCmd('off')         
        elif maxPower *0.6 >= totalPower:
            for item in ComputerMngt.compList.values():
                if item.status == ComputerInfo.Status.OFF:
                    item.powerCmd('on')
                    break
            

            

    
        