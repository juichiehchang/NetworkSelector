import tkinter as tk
from tkinter import ttk
from set_pw import pw
import time
from connect_fastest import traverse as fastest
import os
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        super().title("wifi connection")
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand = True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # wifi list from iwlist
        self.t = fastest("wlp3s0")#list of wifis

        
        self.frames = {}
        """
        frame = StartPage(self.container, self)
        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky ="nsew")
        """
        for F in (StartPage, PageOne, PageTwo):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky = "nsew")
        """
        frame = PageTwo(self.container, self)
        self.frames[PageTwo] = frame
        frame.grid(row=0, column=0, sticky="nsew")  # 四个页面的位置都是 grid(row=0, column=0), 位置重叠，只有最上面的可见！！
        """
        self.show_frame(StartPage)
        #self.destroy()
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise() # 切换，提升当前 tk.Frame z轴顺序（使可见）！！此语句是本程序的点睛之处

class StartPage(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root

        # password dicts
        self.p = pw()

        #aggregate SSIDs
        wifiList = []
        for wifi in root.t.wifi_list:
            if 'Authentication Suites (1)' in wifi:
                if wifi['Authentication Suites (1)'] == "psk":
                    wifiList.append(wifi["ESSID"] + " (PSK)")
                else:
                    wifiList.append(wifi["ESSID"] + " (802.1x)")
            else:
                wifiList.append(wifi["ESSID"])
        self.wifi_listBox(wifiList)##change to real ssid list!!
        self.create_widgets()
        self.description()

        button1 = ttk.Button(self, text="Next", command=lambda: [self.toPageOne()]).grid(row = 3, column = 2)
    
    def toPageOne(self):

        time.sleep(.03)
        self.p.dump()
        self.root.t.get_passwd()
        
        #init PageOne
        """
        frame = PageOne(self.root.container, self.root)
        self.root.frames[PageOne] = frame
        frame.grid(row=0, column=0, sticky ="nsew")
        """
        

        ##Start testing wifi speed
        self.root.t.try_all()
        self.root.t.speedLists.sort(key = lambda sp: sp[1], reverse=True)
        print(self.root.t.speedLists)
        self.root.show_frame(PageOne)

    def create_widgets(self):
        #QUIT botton: exit the window
        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.root.destroy)
        self.quit.grid(row = 3, column = 1)
        #EDIT button: enter user name and password
        self.edit = tk.Button(self, text="EDIT", command=self.enter).grid(row = 3, column = 0)

    def description(self):#display steps to enter user name and pwd
        self.des1 = tk.Label(self, height = 1, width = 25, text = "Description")
        self.des1.grid(row = 1, column = 1, columnspan = 2)
        self.des2 = tk.Label(self, height = 9, width = 25, justify = "left", anchor = "n")
        self.des2["text"] = "Before testing wifi speed, please\nenter the wifi passwords for\nevery access point if necessary."
        self.des2.grid(row = 2, column = 1, columnspan = 2)

    def wifi_listBox(self, wifis):##list all scanned wifis
        self.comment = tk.Label(self, text = 'available wifi').grid(row = 0, column = 0)
        self.wifiList = tk.Listbox(self, height = 20)
        for item in wifis:#insert wifi iteratively
            self.wifiList.insert(1, item)
        self.wifiList.grid(row = 1, column = 0, rowspan = 2)

    def enter(self):
        #create pop-up window
        self.popup = tk.Toplevel(self)
        self.popup.title("edit")
        #handle events
        self.index = self.wifiList.curselection()
        if len(self.index) == 0:#No selection
            self.warning = tk.Label(self.popup, text = "Please select a network from the list").pack()
        else:#jump to enter section, require both user name and password by default
            self.ssid = self.wifiList.get(self.index[0])
            print(self.ssid)
            #create user name and password entry
            self.str1 = tk.StringVar()
            self.str2 = tk.StringVar()
            self.user = tk.Label(self.popup, text = "username:").grid(row = 0, column = 0)
            self.user_entry = tk.Entry(self.popup, textvariable = self.str1, borderwidth = 2, relief = "groove").grid(row = 0, column = 1)

            self.pwd  = tk.Label(self.popup, text = "password:").grid(row = 1, column = 0)
            self.pwd_entry = tk.Entry(self.popup, textvariable = self.str2, borderwidth = 2, relief = "groove").grid(row = 1, column = 1)
            #ok button
            self.ok = tk.Button(self.popup, text = "OK", command = self.saveInfo).grid(row = 2, column = 1)

    def saveInfo(self):##save user name and password
        identity = self.str1.get()
        password = self.str2.get()
        if identity:
            # eap
            self.p.add_eap(self.ssid.split()[0], identity, password)
        else:
            # psk
            self.p.add_psk(self.ssid.split()[0], password)
            
        print(self.ssid)
        self.popup.destroy()
        

class PageOne(tk.Frame):#Switch from PageOne to PageTwo by calling <Application.show_frame(PageTwo)>
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.wait = tk.Label(self, text = "Please wait...").pack()
        self.create_widgets()
        
        #button1 = ttk.Button(self, text="Next", command=lambda: root.show_frame(PageTwo)).pack()
        
        # get password from file
        # try all connections
    def create_widgets(self):
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT,fill=tk.Y)

        self.text = tk.Text(self,yscrollcommand=self.scrollbar.set)
        for wifi in self.root.t.speedLists:
            self.text.insert("end", "ssid: {} Download speed: {}Mb".format(wifi[0], wifi[1]))
        self.text.pack(side=tk.LEFT,fill=tk.BOTH)

        self.scrollbar.config(command=self.text.yview)
        
        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.root.destroy)
        self.quit.pack(side="bottom")

class PageTwo(tk.Frame):#display results
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.wait = tk.Label(self, text = "testing result").pack()
        self.speeds = [("ok", 3, 4)]
        #By default use 3-entry tuple to store 1.ssid 2. upload speed 3. download speed
        for i in self.speeds:
            self.label = tk.Label(self, text = "ssid:{} upload speed:{} download speed:{}".format(i[0], i[1], i[2])).pack()
        self.create_widgets()

    def create_widgets(self):
        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.root.destroy)
        self.quit.pack(side="bottom")

#root = tk.Tk()
if __name__ == '__main__':
    app = Application()
    app.mainloop()


