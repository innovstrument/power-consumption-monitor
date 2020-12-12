from ServerInfo import Computer
from ServerInfo import Status
from tkinter import ttk
from tkinter import *
from tkinter.ttk import Treeview
from tkinter import messagebox
from time import *
from tkinter import PhotoImage
from threading import *
import re
import sys
from PIL import Image, ImageTk
class ServerListUI(Treeview):
    #lables = ['IP Addr', 'User','Password', 'Power Consumption', 'Status','Last Update']
    def __init__(self, master, lables, **kw):
        
        self.serversDict = {}
        self.scheduleList = []
        Treeview.__init__(*(self, master), **kw)
        self._lables = lables
        for i in lables:
            #self.heading(i, text = i)
            self.column(i, width = 150)
        self.column('#0',width = 40)
        #self.heading(0, image = self.checkedImage)
        #i = self.insert('', 'end',values = ('10.100.0.50','read','read','read'),tags = 'unchecked')
        #print(self.heading(column=0))
        #self.set('I001',0,value = self.checkedImage)
        self.bind('<Button 1>', self.checkHandler)

    def checkHandler(self, event):        
        rowid = self.identify_row(event.y)
        colid = self.identify_column(event.x)
        print(self.item(rowid, 'tags'))
        #self.item(rowid,tags = tags)
        print(self.serversDict[rowid])
        if colid == '#0':
            tag = self.item(rowid, 'tags')
            if  tag[0] == 'checked':
                self.item(rowid, tags = 'unchecked')
                self.scheduleList.remove(rowid)
                self.serversDict[rowid].proirity(-1)
            else:
                self.item(rowid, tags = 'checked')
                self.scheduleList.append(rowid)
                self.serversDict[rowid].proirity(1)

    def scheduleHandler(self, on:str):
        for i in self.scheduleList:
            self.serversDict[i].powerCmd(on)

    def add(self, server:Computer):        
        return self.insert('', 'end', values = server.getInfo(),tags = "unchecked")
    
    def edit(self,selection:str, server:Computer):
        info = server.getInfo()
        for i in range (len(info)):
            self.set(selection, column=i, value=info[i])
    
    def totalPower(self) ->float:
        s = self.get_children()
        total = 0
        for i in s:
            total += self.item(i,'values')[3]
        return total

    def __serverInfoEnterHelper(self, server:Computer = None):
        s = []
        inputFrame = Toplevel()
        inputFrame.title('Server Info')

        entryLabels = self._lables[0:3]
        entrys = []
        for i in range(3):
            e = Entry(inputFrame)
            if server:
                e.insert(0,server.getInfo()[i])
            entrys.append(e)
            entryLabel = Label(inputFrame,text = str(entryLabels[i] + ':'))
            entrys[i].pack()
            entryLabel.pack()

        def validateIP(ipAddr:str) ->bool:
            regex = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
            return regex.match(ipAddr)
        
        def submitButtonHandler(s):
            ipAddr = entrys[0].get()
            userName = entrys[1].get()
            password = entrys[2].get()
            if ipAddr and validateIP(ipAddr) and password and userName:
                s.append(Computer(entrys[0].get(),entrys[1].get(),entrys[2].get()))
                inputFrame.destroy()
            else: 
                messagebox.showwarning("Format error",message="Worng Enter Format")
        
        submit = Button(inputFrame,text = 'submit',command = lambda : submitButtonHandler(s = s))
        submit.pack()
        
        inputFrame.wait_window()
        if len(s):  
            return s[0]
        else:
            return None
    
    def addNewServerHandler(self, event=None):
        server = self.__serverInfoEnterHelper()
        if not server:
            return
        selection = self.add(server)
        self.serversDict[selection] = server
        t = Thread(target=self.__threadUpd, args=(selection, server))
        t.setDaemon(True)
        t.start()

    def __threadUpd(self, selection:str, server:Computer):
        while True:
            server.getPower()
            #print(s)
            #if s == 0:
            self.__updHelper(selection,server)
            self.totalPower()
            sleep(5)

    def __updHelper(self,selection:str, server:Computer):
        s = server.getInfo()
        for i in range(len(s)):
            self.set(selection, column = i, value=s[i])

    def getMinVoltage(self)->float:
        minV = sys.maxsize
        for item in self.serversDict.values():
            minV = min(item.minVoltage, minV)
        return minV

    def closeServer(self):
        s = None
        priority = -1
        for server in self.serversDict.values():
            if server.priority > priority and server.status == Status.ON:
                s = server
                priority = server.priority
        if priority >0:
            s.powerCmd('off')

    def openServer(self):
        s = None
        priority = sys.maxsize
        for server in self.serversDict.values():
            if server.priority < priority and server.status == Status.OFF:
                s = server
                priority = server.priority
        if priority < sys.maxsize:
            s.powerCmd('on')
    
if __name__ == "__main__":
    top = Tk()
    lables = ['IP Addr', 'User','Password', 'Power Consumption', 'Status','Last Update']
    t = ServerListUI(top, lables = lables, column = lables)
    style=ttk.Style(t)
    style.configure('Treeview', rowheight = 30)
  

    checkedImage = Image.open("checked.png")
    checkedImage = ImageTk.PhotoImage(checkedImage)
    uncheckedImage = Image.open("unchecked.png")
    uncheckedImage = ImageTk.PhotoImage(uncheckedImage)
    t.tag_configure('checked', image = checkedImage)
    t.tag_configure('unchecked', image = uncheckedImage)

    for i in lables:
        t.heading(i, text = i)
    t.pack()
    t.addNewServerHandler(None)
    top.mainloop()