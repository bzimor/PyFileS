import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from collections import OrderedDict
from configparser import ConfigParser

class ExtSetting(tk.Frame):
    def __init__(self, master, tab):
        tk.Frame.__init__(self, master)
        self.top = tk.Toplevel()
        self.top.resizable(False, False)
        self.top.geometry(set_size(self.top, 350, 450))
        self.top.title("Settings")

        self.file = 'Config.ini'
        self.sec = 'File extensions'
        self.tab = tab
        self.editthis = False
        #self.master = master
        
        self.tbRoot = ttk.Notebook(self.top)
        self.tbRoot.pack(fill='both', expand=True)
        self.tbFile = ttk.Frame(self.tbRoot, width=350, height=380)
        self.tbSkip = ttk.Frame(self.tbRoot)
        self.tbRoot.add(self.tbFile, text='File types')
        self.tbRoot.add(self.tbSkip, text='Skipped folders/files')
        self.tbRoot.select(self.tab)

        self.frTypes = ttk.LabelFrame(self.tbFile, text='File categories', width=280, padding=(5, 5))
        self.frTypes.grid(row=0, column=0, sticky='nswe', padx=(3, 3), pady=(3, 3))
        self.frExt = ttk.LabelFrame(self.tbFile, text='File extensions', width=50, padding=(5, 5))
        self.frExt.grid(row=0, column=1, sticky='nse', padx=(3, 3), pady=(3, 3))
        self.frTypes.columnconfigure(0, weight=1)
        self.frTypes.columnconfigure(1, weight=0)

        #File types
        self.listTypes = tk.Listbox(self.frTypes, exportselection=0, width=15, height=20)
        self.listTypes.grid(row=0, column=0, columnspan=3, sticky='nswe')
        self.entryType = ttk.Entry(self.frTypes)
        self.entryType.grid(row=1, column=0, sticky='nswe', padx=(0, 5), pady=(5, 0))
        self.btnTypeadd = ttk.Button(self.frTypes, text="OK", width=6, command=self.changetype)
        self.btnTypeadd.grid(row=1, column=1, sticky='ns', padx=(0, 5), pady=(5, 0))
        self.scroll = ttk.Scrollbar(self.frExt, orient='vertical')
        self.listExt = tk.Listbox(self.frExt, width=18, height=20, yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.listExt.yview)
        self.scroll.grid(row=0, column=1, sticky='nse')
        self.listExt.grid(row=0, column=0, sticky='nswe')
        self.frmExt = ttk.Frame(self.frExt)
        self.frmExt.grid(row=1, column=0, columnspan=2, padx=(0, 0))
        self.entryExt = ttk.Entry(self.frmExt, width=8)
        self.entryExt.grid(row=0, column=0, sticky='nswe', padx=(0, 5), pady=(5, 0))
        self.btnExtadd = ttk.Button(self.frmExt, text="+", width=4, command=self.changeext)
        self.btnExtadd.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=(5, 0))
        self.btnExtdel = ttk.Button(self.frmExt, text="-", width=4, command=self.delext)
        self.btnExtdel.grid(row=0, column=2, sticky='ns', pady=(5, 0))
        self.frBottom = ttk.Frame(self.tbFile)
        self.frBottom.grid(row=1, column=0, columnspan=2, sticky='nswe')
        self.labelB = ttk.Label(self.frBottom, 
                           text='To delete an item in file categories, \njust delete extensions belong to it')
        self.labelB.grid(row=0, column=0, sticky='nswe', padx=(5, 0))
        self.labelB.config(font=('Arial', 8))
        self.btnSave = ttk.Button(self.frBottom, text='Save', width=10, command=self.updatefile)
        self.btnSave.grid(row=0, column=1, sticky='nse', padx=(20, 0), pady=(3, 3))
        self.btnReset = ttk.Button(self.frBottom, text='Reset', width=10, command=self.resetlist)
        self.btnReset.grid(row=0, column=2, sticky='nse', padx=(5, 0), pady=(3, 3))

        #Skip section
        self.skipfrm = SkipSetting(self.tbSkip, self.top)

        self.listTypes.bind('<<ListboxSelect>>', self.filterext)
        self.listTypes.bind('<Double-1>', self.edittype)
        self.entryType.bind('<Return>', self.changetype)
        self.listExt.bind('<Double-1>', self.editext)
        self.entryExt.bind('<Return>', self.changeext)
        self.listExt.bind('<KeyPress-Delete>', self.delext)

        self.settypes()
        self.top.transient(master)
        self.top.grab_set()
        master.wait_window(self.top)

    def settypes(self):
        self.typedict = {}
        self.fullexts = []
        self.config = ConfigParser()
        self.config.read(self.file)
        for item in self.config.items(self.sec):
            if item[1] not in self.typedict:
                self.typedict[item[1]]=[]    
            self.typedict[item[1]].append(item[0])
            self.fullexts.append(item[0])
        self.fulldict = OrderedDict(self.config.items(self.sec))
        self.updatelists()

    def updatelists(self, index=0):
        self.listTypes.delete(0, 'end')
        self.listTypes.insert('end', "All")
        ftypes =list(self.typedict.keys())
        for item in sorted(ftypes):
            self.listTypes.insert('end', item)
        for item in sorted(self.fullexts):
            self.listExt.insert('end', item)
        self.listTypes.select_set(index)
        self.filterext()
        
    def filterext(self, event=None):
        index = self.listTypes.curselection()[0]
        selection = self.listTypes.get(index)
        self.listExt.delete(0, 'end')
        self.entryType.delete(0, 'end')
        if selection == "All":
            for item in sorted(self.fullexts):
                self.listExt.insert('end', item)
        else:
            lst = sorted(self.typedict[selection])
            for item in lst:
                self.listExt.insert('end', item)

    def edittype(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        selected = w.get(index)
        if selected != "All":
            self.entryType.delete(0, 'end')
            self.entryType.insert(0, selected)
            self.editthis = True      

    def changetype(self, event=None):
        name = self.entryType.get().strip()
        index = self.listTypes.curselection()[0]
        if name != "All" and name != '':
            if self.editthis:
                oldname = self.listTypes.get(index)
                self.entryType.delete(0, 'end')
            else:
                oldname = None
            self.updatedict(name, oldname, False, self.editthis)

    def editext(self, event):
        w = event.widget
        index = w.curselection()[0]
        selected = w.get(index)
        if self.listTypes.curselection()[0]!=0:
            self.entryExt.delete(0, 'end')
            self.entryExt.insert(0, selected)
            self.editthis = True
        else:
            self.mboxes(1, 1)

    def changeext(self, event=None):
        name = self.entryExt.get()
        if name.startswith('.') and len(name.strip())>1:
            if self.listTypes.curselection()[0]!=0:
                if name not in self.fullexts:
                    if name and self.editthis:
                        index = self.listExt.curselection()[0]
                        oldname = self.listExt.get(index)
                        self.listExt.delete(index)
                        self.listExt.insert(index, name)
                        self.entryExt.delete(0, 'end')
                    else:
                        self.listExt.insert('end', name)
                        self.entryExt.delete(0, 'end')
                        oldname = None
                    self.updatedict(name, oldname, True, self.editthis)
                else:
                    self.mboxes(1, 2, name)
            else:
                self.mboxes(1, 1)
        else:
            self.mboxes(1, 3)

    def updatedict(self, name, oldname=None, ext=False, edit=False):
        index = self.listTypes.curselection()[0]
        if not ext:
            if edit and (name != oldname != ""):
                self.typedict[name] = self.typedict[oldname]
                del self.typedict[oldname]
                for ext in self.typedict[name]:
                    self.fulldict[ext] = name
            else:
                if name not in self.typedict:
                    self.typedict[name]=[]
                    if '' in self.fulldict:
                        self.fulldict[''].append(name)
                    else:
                        self.fulldict[''] = [name]
        else:
            selected = self.listTypes.get(index)
            if edit and (name != oldname != ""):
                num = self.typedict[selected].index(oldname)
                self.typedict[selected].remove(oldname)
                self.typedict[selected].insert(num, name)
                nm = self.fullexts.index(oldname)
                self.fullexts.remove(oldname)
                self.fullexts.insert(nm, name)
                del self.fulldict[oldname]
            else:
                if name not in self.typedict[selected]:
                    self.typedict[selected].append(name)
                    self.fullexts.append(name)
            self.fulldict[name] = selected
        self.editthis = False
        self.updatelists(index)
        self.btnSave.config(state='normal')
        
    def delext(self, event=None):
        if len(self.listExt.get(0, 'end')) != 0:
            index1 = self.listTypes.curselection()[0]
            index2 = self.listExt.curselection()[0]
            if index1 != 0:
                selected = self.listTypes.get(index1)
                oldname = self.listExt.get(index2)
                reply = self.mboxes(2, 1, oldname)
                if reply:
                    self.typedict[selected].remove(oldname)
                    self.fullexts.remove(oldname)
                    del self.fulldict[oldname]
                    self.listExt.delete(index2)
                    self.updatelists(index1)
                    if index2 != 0:
                        self.listExt.select_set(index2-1)
                        self.listExt.see(index2-1)
                    else:
                        self.listExt.select_set(0)
            else:
                self.mboxes(1, 1)
            self.btnSave.config(state='normal')

    def mboxes(self, mtype, m, ext=None):
        if mtype == 1:
            if m==1:
                text = 'Please, first choose file category'
            elif m==2:
                cat = self.fulldict[ext]
                text = 'This file extension is already exist in %s!' %(cat)
            elif m==3:
                text = 'Please, enter valid file extension'
            tk.messagebox.showwarning(title="Warning", message=text)
        elif mtype == 2:
            text = 'Do you want to delete extension "%s" ?' %(ext)
            answer = tk.messagebox.askyesno(title="File extension", message=text)
            return answer
        
    def updatefile(self):
        self.config[self.sec]={}
        sorteddict = OrderedDict(sorted(self.fulldict.items(), key=lambda itm: itm[0]))
        for k, v in sorteddict.items():
            if k != '':
                self.config.set(self.sec, k, v)
            else:
                continue
        with open(self.file, 'w') as file:
            self.config.write(file)
        self.top.destroy()
        
    def resetlist(self):
        self.settypes()
        self.btnSave.state(['disabled'])

class SkipSetting(tk.Frame):
    """write something"""
    def __init__(self, master, top):
        tk.Frame.__init__(self, master)
        self.configfile = 'Config.ini'
        self.known = tk.IntVar()
        self.edit = False
        self.master = master
        self.top = top
        self.hidden = tk.IntVar()
        self.skipped = tk.IntVar()

        #Skipped tab
        self.frHidden = ttk.LabelFrame(master, text='Show folders/files', padding=(5, 5))
        self.frHidden.grid(row=0, column=0, sticky='nswe', padx=(3, 3), pady=(3, 3))
        self.frSkip = ttk.LabelFrame(master, text='These folders/files will be skipped', padding=(5, 5))
        self.frSkip.grid(row=1, column=0, sticky='nswe', padx=(3, 3), pady=(3, 3))

        self.checkKnown = ttk.Checkbutton(self.frHidden, text="Show only known file types",
                                              onvalue=1, offvalue=0, variable=self.known)
        self.checkKnown.pack(side='top', anchor="w")
        self.checkHidden = ttk.Checkbutton(self.frHidden, text="Show hidden folders/files",
                                              onvalue=1, offvalue=0, variable=self.hidden)
        self.checkHidden.pack(anchor="w")
        self.checkSkip = ttk.Checkbutton(self.frHidden, text="Skip folders/files listed below",
                                              onvalue=1, offvalue=0, variable=self.skipped, 
                                              command=self.toggle_list)
        self.checkSkip.pack(anchor="w")
        self.scrollskip = ttk.Scrollbar(self.frSkip, orient='vertical')
        self.listSkip = tk.Listbox(self.frSkip, width=50, height=14, yscrollcommand=self.scrollskip.set)
        self.scrollskip.config(command=self.listSkip.yview)
        self.scrollskip.grid(row=0, column=1, sticky='nse')
        self.listSkip.grid(row=0, column=0, sticky='nswe')
        self.frmSkip = ttk.Frame(self.frSkip)
        self.frmSkip.grid(row=2, column=0, columnspan=2, padx=(0, 0))
        self.entrySkip = ttk.Entry(self.frmSkip, width=40)
        self.entrySkip.grid(row=0, column=0, sticky='nswe', padx=(0, 5), pady=(5, 0))
        self.btnSkipadd = ttk.Button(self.frmSkip, text="+", width=4, command=self.change_skip)
        self.btnSkipadd.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=(5, 0))
        self.btnSkipdel = ttk.Button(self.frmSkip, text="-", width=4, command=self.del_skip)
        self.btnSkipdel.grid(row=0, column=2, sticky='ns', pady=(5, 0))
        self.skBottom = ttk.Frame(master)
        self.skBottom.grid(row=2, column=0, columnspan=2, sticky='nswe')
        self.skpSave = ttk.Button(self.skBottom, text='Save', width=10, command=self.save_list)
        self.skpSave.grid(row=0, column=0, sticky='nse', padx=(190, 0), pady=(3, 3))
        self.skpReset = ttk.Button(self.skBottom, text='Reset', width=10, command=self.reset_list)
        self.skpReset.grid(row=0, column=1, sticky='nse', padx=(5, 0), pady=(3, 3))


        self.listSkip.bind('<Double-1>', self.edit_skip)
        self.listSkip.bind('<KeyPress-Delete>', self.del_skip)
        self.entrySkip.bind('<Return>', self.change_skip)
        self.get_from_ini()
        self.toggle_list()
        

    def get_from_ini(self):
        self.skiplist=[]
        self.config = ConfigParser()
        self.config.read(self.configfile)
        sect = 'Skipped items'    
        self.known.set(self.config.getint(sect, 'ShowOnlyKnownItems'))
        self.hidden.set(self.config.getint(sect, 'ShowHiddenItems'))
        self.skipped.set(self.config.getint(sect, 'SkipListedItems'))
        for item in self.config.items('SkippedList'):
            self.skiplist.append(item[1])
        self.update_list()

    def update_list(self):
        self.skiplist = sorted(list(set(self.skiplist)))
        self.listSkip.delete(0, 'end')
        for item in self.skiplist:
            self.listSkip.insert('end', item)

    def toggle_list(self):
        if self.skipped.get()==0:
            self.listSkip.config(state='disabled')
            self.entrySkip.config(state='disabled')
            self.btnSkipdel.config(state='disabled')
            self.btnSkipadd.config(state='disabled')
        else:
            self.listSkip.config(state='normal')
            self.entrySkip.config(state='normal')
            self.btnSkipdel.config(state='normal')
            self.btnSkipadd.config(state='normal')

    def edit_skip(self, event):
        index = self.listSkip.curselection()[0]
        item = self.listSkip.get(index)
        self.entrySkip.delete(0, 'end')
        self.entrySkip.focus_set()
        self.listSkip.select_set(index)
        self.entrySkip.insert(0, item)
        self.edit = True

    def change_skip(self, event=None):
        newname = self.entrySkip.get()
        if newname:
            if self.edit:
                index = self.listSkip.curselection()[0]
                oldname = self.listSkip.get(index)
                self.entrySkip.delete(0, 'end')
                listind = self.skiplist.index(oldname)
                self.skiplist.remove(oldname)
                self.skiplist.insert(listind, newname)
                self.edit = False
            else:
                self.skiplist.append(newname)
                self.entrySkip.delete(0, 'end')
            self.update_list()
            self.skpSave.config(state='normal')



    def del_skip(self, event=None):
        if len(self.listSkip.get(0, 'end')) != 0:
            index = self.listSkip.curselection()[0]
            oldname = self.listSkip.get(index)
            text = 'Do you want to delete "%s" from list?' %(oldname)
            answer = tk.messagebox.askyesno(title="Skip list", message=text)
            if answer:
                self.skiplist.remove(oldname)
                self.update_list()
                if index !=0:
                    self.listSkip.select_set(index-1)
                else:
                    self.listSkip.select_set(0)
            self.skpSave.config(state='normal')

    def save_list(self):
        sect = 'Skipped items'
        self.config.set(sect, 'ShowOnlyKnownItems', str(self.known.get()))
        self.config.set(sect,'ShowHiddenItems', str(self.hidden.get()))
        self.config.set(sect, 'SkipListedItems', str(self.skipped.get()))
        self.config['SkippedList']={}
        for k, v in enumerate(sorted(self.skiplist)):
            self.config['SkippedList'][str(k)] = str(v)
        with open(self.configfile, 'w') as configfile:
            self.config.write(configfile)
        self.top.destroy()

    def reset_list(self):
        self.get_from_ini()
        self.skpSave.state(['disabled'])


#window size setting
def set_size(win, w=0, h=0, absolute=True):
    winw = win.winfo_screenwidth()
    winh = win.winfo_screenheight()
    win_ratio = 0.8
    if not absolute:
        w = int(winw * win_ratio)
        h = int(winh * win_ratio)
        screen = "{0}x{1}+{2}+{3}".format(w, h, str(int(winw*0.1)),
                                          str(int(winh*0.05)))       
    else:
        screen = "{0}x{1}+{2}+{3}".format(w, h, str(int((winw-w)/2)),
                                          str(int((winh-h)/2)))
    return screen
