from ServerMgt import *
from ServerInfo import *
from tkinter import ttk
from tkinter import *
from DisplayAndControlFrame import *
from PIL import Image, ImageTk
class Application(Frame):
    def __init__(self, master, **kw):
        Frame.__init__(*(self, master), **kw)
        lables = ['IP Addr', 'User','Password', 'Power Consumption', 'Status','Last Update']

        self.__list = ServerListUI(self,lables= lables, column = lables)
        style=ttk.Style(self.__list)
        style.configure('Treeview', rowheight = 30)
        self.checkedImage = Image.open("checked.png")
        self.checkedImage = ImageTk.PhotoImage(self.checkedImage)
        self.uncheckedImage = Image.open("unchecked.png")
        self.uncheckedImage = ImageTk.PhotoImage(self.uncheckedImage)
        self.__list.tag_configure('checked', image = self.checkedImage)
        self.__list.tag_configure('unchecked', image = self.uncheckedImage)
        for i in lables:
            self.__list.heading(i, text = i)
        
        self.__list.pack()
        
        
        self.displayFrame = DisplayFrame(self,self.__list)
        self.displayFrame.pack()

    
        

if __name__ == "__main__":
    t = Tk(None)
    tt = Application(t)

    
    tt.pack()
    t.mainloop()
