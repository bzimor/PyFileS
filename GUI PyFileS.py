import tkinter as tk
from tkinter import ttk
import os
from Settings import set_size, ExtSetting
import Filesio as fio
from configparser import ConfigParser
import time
import ctypes
from collections import OrderedDict
import threading
import wckToolTips
from Tree import DirTree
import tkinter.filedialog as filedialog
from tkinter import messagebox
import subprocess

 
#############################################################################
########################-----class MainWindow-----###########################

class MainWindow:
    def __init__(self, master):
        
        # Main window settings
        master.title("PyFileS")
        master.geometry(set_size(master, absolute=False))
        master.resizable(True, True)
        self.s = ttk.Style()

        #Global variables
        hierarchy=tk.StringVar()
        hierarchy.set(1)
        self.defview=tk.StringVar()
        self.defview.set("Directory view")
        self.master = master
        self.dt = DirTree()
        self.images = self.dt.images
        self.browsemode = False
        hidden = tk.IntVar() #delete this
        
        #Frames
        self.frameSide = ttk.Frame(master, width=180, relief="solid")
        self.frameSide.grid(row=0, column=0, rowspan=2, sticky="nswe")
        self.frameMain = ttk.Frame(master, width=780, height=660, relief="solid")
        self.frameMain.grid(row=0, column=1, sticky="nswe")
        self.frameInfo = ttk.Frame(master, width=800, height=32)
        self.frameInfo.grid(row=1, column=1, sticky="swe")
        self.frameLog = ttk.Frame(master, height=20)
        self.frameLog.grid(row=2, column=0, columnspan=2, sticky="we")
        self.frameManage = ttk.Frame(self.frameMain, width=40, height=620, relief="solid")
        self.frameManage.grid(row=0, column=2, rowspan=2, sticky="ne")
        self.frameInfo.grid_propagate(False)
        master.rowconfigure(0, weight=1)
        #master.rowconfigure(1, weight=1)
        #master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        self.frameMain.grid_propagate(False)
        master.grid_propagate(False)
        self.frameMain.rowconfigure(0, weight=1)
        self.frameMain.columnconfigure(0, weight=1)
        self.frameInfo.rowconfigure(1, weight=1)
        self.frameInfo.columnconfigure(0, weight=1)
        self.frameLog.columnconfigure(0, weight=1)
        

        # Menubar
        master.option_add('*tearOff', False)
        self.menubar = tk.Menu(master)
        master.config(menu = self.menubar)
        self.file = tk.Menu(self.menubar)
        self.edit = tk.Menu(self.menubar)
        self.options = tk.Menu(self.menubar)
        help_ = tk.Menu(self.menubar)

        self.menubar.add_cascade(menu = self.file, label = 'File')
        #self.menubar.add_cascade(menu = self.edit, label = 'Edit')
        self.menubar.add_cascade(menu = self.options, label = 'Options')
        self.menubar.add_cascade(menu = help_, label = 'Help')
        
        self.file.add_command(label = 'New file', command=lambda: self.save_to_new(True))
        self.file.add_command(label = 'Open...', command = self.show_dbtree)
        self.file.add_separator()
        self.file.add_command(label = 'Save')
        self.file.add_command(label = 'Save as...', command = lambda: print('Saving as File...'))

        self.options.add_command(label = 'File Extensions', command =self.catsettings)
        self.options.add_command(label = 'Treeview setting', command =lambda: self.catsettings(1))
        self.options.add_command(label = 'Database setting', command =lambda: self.catsettings(1))
        
        self.file.entryconfig('New file', accelerator = 'Ctrl+N')
        self.file.entryconfig('Open...', accelerator = 'Ctrl+O')
        self.file.entryconfig('Save', accelerator = 'Ctrl+S')
        self.file.entryconfig('Save as...', accelerator = 'Ctrl+Shift+S')

        #Right click menu
        self.aMenu = tk.Menu(master, tearoff=0)
        self.aMenu.add_command(label='Open in explorer', command=self.open_expl)
        self.addto = tk.Menu(self.aMenu, tearoff=0)
        self.addto.add_command(label='Current database', command=self.save_to_h5)
        self.addto.add_command(label='New database', command=self.save_to_new)
        self.aMenu.add_cascade(label='Add to...', menu=self.addto)
        


        # Widgets

        ## Treeview
        self.dirtree = ttk.Treeview(self.frameMain, columns=("fullpath","type","size", "modified", "note", "category"))
        self.dirtree.grid(row=0, column=0, sticky ="nsew")
        self.dirtree.heading("#0", text="Locations")
        self.dirtree.heading("type", text="Type")   
        self.dirtree.heading("modified", text="Modified date")   
        self.dirtree.heading("size", text="File size", anchor="center")   
        self.dirtree.heading("note", text="Notes")   
        self.dirtree.heading("category", text="Category")   
        self.dirtree.heading("fullpath", text="Full path", anchor="center")   
        #self.dirtree.column("#0", minwidth=110, width=180, stretch=True)
        self.dirtree.column("type",minwidth=20, width=110, stretch=False, anchor="center")
        self.dirtree.column("modified",minwidth=20, width=110, stretch=False, anchor="center") 
        self.dirtree.column("size",minwidth=20, width=110, stretch=False, anchor="e")
        self.dirtree.column("note",minwidth=20, width=110, stretch=False, anchor="center")
        self.dirtree.column("category",minwidth=20, width=110, stretch=False, anchor="center")
        #self.dirtree.column("fullpath",minwidth=110, width=180, stretch=True, anchor="w")
        self.dirtree.tag_configure('even', background='#e0e2e5')
        #heading contextmenu

        self.col2 = tk.IntVar()
        self.col3 = tk.IntVar()
        self.col4 = tk.IntVar()
        self.col5 = tk.IntVar()
        self.col6 = tk.IntVar()
        self.col7 = tk.IntVar()
        self.read_config()
        self.headMenu = tk.Menu(master, tearoff=0)
        self.headMenu.add_checkbutton(label=self.dirtree.heading("modified")['text'], variable=self.col2, onvalue=1, offvalue=0, command=self.toggle_cols)
        self.headMenu.add_checkbutton(label=self.dirtree.heading("size")['text'], variable=self.col3, onvalue=1, offvalue=0, command=self.toggle_cols)
        self.headMenu.add_checkbutton(label=self.dirtree.heading("type")['text'], variable=self.col4, onvalue=1, offvalue=0, command=self.toggle_cols)
        self.headMenu.add_checkbutton(label=self.dirtree.heading("category")['text'], variable=self.col5, onvalue=1, offvalue=0, command=self.toggle_cols)
        self.headMenu.add_checkbutton(label=self.dirtree.heading("note")['text'], variable=self.col6, onvalue=1, offvalue=0, command=self.toggle_cols)
        self.headMenu.add_checkbutton(label=self.dirtree.heading("fullpath")['text'], variable=self.col7, onvalue=1, offvalue=0, command=self.toggle_cols)
        
        ## Scrollbars
        self.vsb = ttk.Scrollbar(self.frameMain, orient="vertical", command=self.dirtree.yview)
        self.hsb = ttk.Scrollbar(self.frameMain, orient="horizontal", command=self.dirtree.xview)
        self.vsb.grid(row=0, column=1, sticky="nse")
        self.hsb.grid(row=1, column=0, sticky="sew")
        self.dirtree.config(yscrollcommand=lambda f, l: self.autoscroll(self.vsb, f, l))
        self.dirtree.config(xscrollcommand=lambda f, l:self.autoscroll(self.hsb, f, l))



        ## SideControls

        ### Database list
        self.frameBases = ttk.LabelFrame(self.frameSide, text="Saved database list", padding=(10, 10))
        self.frameBases.grid(row=0, column=0, sticky="nswe", padx=(5,5), pady=(2,5))
        self.btnDOpen = ttk.Button(self.frameBases,  image=self.images['Open20'], command=self.show_dbtree)
        self.btnDOpen.grid(row=0, column=0, padx=(0,1), pady=(1,2))
        self.btnDBAdd = ttk.Button(self.frameBases,  image=self.images['DBAdd'], command=lambda: self.save_to_new(True))
        self.btnDBAdd.grid(row=0, column=1, padx=(0,1), pady=(1,2))
        self.btnDCAdd = ttk.Button(self.frameBases, image=self.images['Add20'], command=lambda: self.save_to_h5(True))
        self.btnDCAdd.grid(row=0, column=2, padx=(0,1), pady=(1,2))
        self.btnDSaveas = ttk.Button(self.frameBases, image=self.images['SaveAs'])
        self.btnDSaveas.grid(row=0, column=3, padx=(0,1), pady=(1,2))
        self.btnDExit = ttk.Button(self.frameBases, image=self.images['Exit'], command=self.close_db)
        self.btnDExit.grid(row=0, column=4, padx=(0,1), pady=(1,2))
        self.btnDDel = ttk.Button(self.frameBases, image=self.images['Del20'], command=self.delete_db)
        self.btnDDel.grid(row=0, column=5, padx=(0,0), pady=(1,2))
        self.dbList = ttk.Treeview(self.frameBases, columns=("fullpath","size", "filesystem", "note"),
                                      displaycolumns="", height=7)
        self.dbList.grid(row=1, column=0, columnspan=6, sticky="nswe")
        self.dbList.heading("#0", text="Databases")
        self.dbList.column("#0", minwidth=20, width=180, stretch=False)
        self.dbList.heading("size", text="Size", anchor="center")   
        self.dbList.column("size",minwidth=20, width=70, stretch=False, anchor="e")
        
        ### Drive list
        self.frameDrives = ttk.LabelFrame(self.frameSide, text="Local drive list", padding=(10, 10))
        self.frameDrives.grid(row=1, column=0, sticky="nswe", padx=(5,5), pady=(2,5))
        #self.btnChangelist = ttk.Button(self.frameDrives, text="Choose database to open")
        #self.btnChangelist.grid(row=0, column=0, padx=(3,3), pady=(1,2))
        self.btnUpdatedr = ttk.Button(self.frameDrives, image=self.images['Refresh'],
                                      command=self.drive_tree)
        self.btnUpdatedr.grid(row=0, column=1, sticky="e", padx=(3,3), pady=(1,2))
        self.driveList = ttk.Treeview(self.frameDrives, columns=("fullpath","size", "filesystem", "note"),
                                      displaycolumns="", height=7)
        self.driveList.grid(row=1, column=0, columnspan=2, sticky="nswe")
        self.drive_tree()
        self.driveList.heading("#0", text="Drives")
        self.driveList.column("#0", minwidth=20, width=180, stretch=False)
        self.driveList.heading("size", text="Size", anchor="center")   
        self.driveList.column("size",minwidth=20, width=70, stretch=False, anchor="e")

        ### Change view
        self.frameShowOpt = ttk.LabelFrame(self.frameSide, text="Change view", padding=(15, 0))
        self.frameShowOpt.grid(row=2, column=0, sticky="nswe", padx=(5,5), pady=(5,5), ipady=3)
        self.style = ttk.Style()
        self.style.configure("TLabelframe.Label", foreground="black")
        #self.checkHierarchy = ttk.Checkbutton(self.frameShowOpt, text="Hierarchical view",
        #                                      onvalue=1, offvalue=0, variable=hierarchy)
        #self.checkHierarchy.pack(anchor="w", pady=(5,5))
        #ttk.Separator(self.frameShowOpt, orient="horizontal").pack(fill="x")
        self.comboView = ttk.Combobox(self.frameShowOpt, textvariable=self.defview,
                                      values=("Directory view", "File type view",
                                              "Chronologic view"))
        self.comboView.pack(fill='x', pady=(5,5))
        #self.radioDir = ttk.Radiobutton(self.frameShowOpt, text="Directory view",
        #                                value="dirview", variable=self.defview)
        #self.radioDir.pack(anchor="w", pady=(5,0))        

        ### Filters and search
        self.tabShowonly = ttk.Notebook(self.frameSide)
        self.tabShowonly.grid(row=3, column=0, sticky="we", padx=(5, 5))
        self.frameTab1 = ttk.Frame(self.tabShowonly)
        self.frameTab2 = ttk.Frame(self.tabShowonly)
        self.tabShowonly.add(self.frameTab2, text="Advanced search")
        self.tabShowonly.add(self.frameTab1, text="Filter files/folders")
        
        #### Filter
        self.checkFolder = ttk.Checkbutton(self.frameTab1, text="Show folders",
                                              onvalue=1, offvalue=0, variable=hidden)
        self.checkFolder.pack(anchor="w", pady=(2,2))
        self.checkFile = ttk.Checkbutton(self.frameTab1, text="Show files",
                                              onvalue=1, offvalue=0, variable=hidden)
        self.checkFile.pack(anchor="w", pady=(2,2))
        ttk.Separator(self.frameTab1, orient="horizontal").pack(fill="x")
        

        #### Search
        self.entrySearch = ttk.Entry(self.frameTab2)
        self.entrySearch.pack(fill="x", padx=(3,3), pady=(5,2))
        self.btnSearch = ttk.Button(self.frameTab2, text="Search")
        self.btnSearch.pack(fill="x", padx=(3,3), pady=(5,2))
        
        ## Search entry
        self.frameConsole = ttk.Frame(self.frameInfo)
        self.frameConsole.grid(row=0, column=0, sticky="nwe")
        self.frameConsole.columnconfigure(0, weight=1)
        self.searchEntry = ttk.Entry(self.frameConsole)
        self.searchEntry.grid(row=0, column=0, sticky='nswe', pady=(2, 4))
        self.btnCopy = ttk.Button(self.frameConsole, text='Copy')
        self.btnCopy.grid(row=0, column=1, sticky='nswe', padx=(3, 0) ,pady=(2, 4))
        self.btnSearch = ttk.Button(self.frameConsole, text='Search')
        self.btnSearch.grid(row=0, column=2, sticky='nswe', padx=(3, 0) ,pady=(2, 4))
        self.btnDown = ttk.Button(self.frameConsole, text='˅', width=5)
        self.btnDown.grid(row=0, column=3, sticky='nswe', padx=(3, 0) ,pady=(2, 4))
        self.btnUp = ttk.Button(self.frameConsole, text='˄', width=5)
        self.btnUp.grid(row=0, column=4, sticky='nswe', padx=(3, 40) ,pady=(2, 4))
        #self.label = tk.Label(self.frameConsole, bd=1, relief="sunken", text="Console:", anchor="w")
        #self.label.pack(fill="x")
        #self.entry = tk.Text(self.frameLog, bd=1)
        #self.entry.pack(fill="both", expand=True)

        ## Statusbar
        self.status = StatusBar(self.frameLog)
        self.status.grid(row=1, column=0, sticky="swe")
        self.status.set("Ready   ")

        ## Buttons    
        self.btAdd = ttk.Button(self.frameManage, image=self.images['Add'], command=self.open_root)
        self.btEdit = ttk.Button(self.frameManage, image=self.images['Edit'])
        self.btDelete = ttk.Button(self.frameManage, image=self.images['Del']) #command=self.additems
        self.btOpen = ttk.Button(self.frameManage, image=self.images['Open'])
        #command=lambda: self.count_tree_items(self.dirtree, self.dirtree.focus())
        self.btSave = ttk.Button(self.frameManage, image=self.images['Save'])
        
        self.btAdd.grid(row=0, column=0, sticky="n")
        self.btEdit.grid(row=1, column=0, sticky="n")
        self.btDelete.grid(row=2, column=0, sticky="n")
        self.btOpen.grid(row=3, column=0, sticky="n")
        self.btSave.grid(row=4, column=0, sticky="n")
        wckToolTips.register(self.btAdd, "This button adds directory")
       
        ## defining options for opening a directory
        self.dir_opt = options = {}
        #self.home = os.path.expanduser('~') #users home directory
        options['initialdir'] = 'C:/'
        options['mustexist'] = False
        options['parent'] = self.master
        options['title'] = 'Choose directory'

        ## defining options for saving and opening file
        self.file_opt = foptions = {}
        foptions['defaultextension'] = '.h5'
        foptions['initialdir'] = 'D:/'
        foptions['filetypes'] = [('H5 files', '.h5'), ('All files', '.*')]
        foptions['parent'] = self.master
        foptions['title'] = 'Open a database'

        self.nfile_opt = nfoptions = {}
        nfoptions['defaultextension'] = '.h5'
        nfoptions['initialdir'] = 'D:/'
        nfoptions['filetypes'] = [('H5 files', '.h5'), ('All files', '.*')]
        nfoptions['initialfile'] = os.environ['COMPUTERNAME']
        nfoptions['parent'] = self.master
        nfoptions['title'] = 'Create a database'

        # Event bindings
        #self.master.bind('<Configure>', self.col_width_set)
        self.dirtree.bind('<<TreeviewOpen>>', self.update_tree)
        self.dbList.bind('<Double-Button-1>', self.open_dbtree)
        self.driveList.bind('<Double-Button-1>', self.open_root)
        self.dirtree.bind("<Button-3>", self.conmenu)
        master.protocol("WM_DELETE_WINDOW", self.app_quit)      
        fio.check_extfile()

    def change_view(self):
        pass

    def col_width_set(self, event=None):
        '''Auto stretch tree column width'''
        self.dirtree.update()
        tree_w = self.dirtree.winfo_width()
        other_w = (self.col2.get() + self.col3.get() + self.col4.get() + self.col5.get() + self.col6.get()) * 110
        if self.col7.get() == 1:
            equi_w = int((tree_w-other_w)/2)
            self.dirtree.column("#0", width=equi_w, stretch=True)
            self.dirtree.column("fullpath", width=equi_w+2, stretch=True)
            self.dirtree.update()
            self.dirtree.column("fullpath", width=equi_w-2, stretch=True)

        else:
            equi_w = int((tree_w-other_w))
            self.dirtree.column("#0", width=equi_w, stretch=True)
            self.dirtree.update()
            self.dirtree.column("#0", width=equi_w-2, stretch=True)

    def open_dbtree(self, event=None):
        if self.dbList.focus():
            self.browsemode = False
            if self.dbList.focus() not in self.dbList.get_children():
                dbitem = self.dbList.item(self.dbList.focus())['text']
                name = self.dbList.parent(self.dbList.focus())
                store = fio.open_store(name)
                view = self.defview.get()
                if view == 'Directory view':
                    self.dt.buildtree(self.dirtree, dbitem, store)
                elif view == 'File type view':
                    self.dt.buildtree_cat(self.dirtree, dbitem, store)
                elif view == 'Chronologic view':
                    self.dt.buildtree_date(self.dirtree, dbitem, store)
                    


    def open_root(self, event=None):
        self.browsemode = True
        if event:
            w = event.widget
            id = w.focus()
        else:
            id =filedialog.askdirectory(**self.dir_opt)
        self.dt.populate_roots(self.dirtree, id)
        #self.sort_tree(self.dirtree, id, 'type', False)

    def update_tree(self, event):
        if self.browsemode:
            w = event.widget
            if len(w.get_children(w.focus())) != 0:
                self.dt.populate_tree(w, w.focus())
                #self.sort_tree(w, w.focus(), 'type', False)

    def sort_tree(self, tree, id, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children(id)]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            tree.move(k, id, index)
        tree.heading(col, command = lambda _col=col: self.sort_tree(tree, id, _col, not reverse))

    def show_dbtree(self):
        dbname = filedialog.askopenfilename(**self.file_opt)
        if dbname:
            store = fio.open_store(dbname)
            self.dt.database_items(dbname, self.dbList, store)

    def save_to_h5(self, btn=False):
        selected = self.dbList.focus()
        if selected:
            if selected in self.dbList.get_children():
                store =selected
            else:
                store =self.dbList.parent(selected)
            if btn:
                df =filedialog.askdirectory(**self.dir_opt)
            else:
                df = self.tid
            cstore = fio.open_store(store)
            self.dt.gettree(df, cstore)
            cstore = fio.open_store(store)
            self.dt.database_items(store, self.dbList, cstore, rebuild=True)
        else:
            pass
    
    def save_to_new(self, add=False):
        new_dbfile = filedialog.asksaveasfilename(**self.nfile_opt)
        if new_dbfile:
            if add:
                cstore = fio.open_store(new_dbfile)
                self.dt.database_items(new_dbfile, self.dbList, cstore)
            else:
                df = self.tid
                new_store = fio.open_store(new_dbfile)
                self.dt.gettree(df, new_store)
                cstore = fio.open_store(new_dbfile)
                self.dt.database_items(new_dbfile, self.dbList, cstore)    

    def delete_db(self):
        selected = self.dbList.focus()
        if selected:
            if selected in self.dbList.get_children():
                reply = self.mboxes(2, 1, selected)
                if reply:
                    os.remove(selected)
                    self.dbList.delete(selected)

            else:
                reply = self.mboxes(2, 1, selected)
                store =self.dbList.parent(selected)
                if reply:
                    df = self.dbList.item(selected)['text']
                    if self.dirtree.get_children():
                        if self.dirtree.get_children()[0]==df and not self.browsemode:
                            self.dirtree.delete(self.dirtree.get_children())
                    store = fio.open_store(store)
                    del store[df]
                    store.close()
                    self.dbList.delete(selected)
        else:
            pass

    def close_db(self):
        selected = self.dbList.focus()
        if selected:
            if selected in self.dbList.get_children():
                store = selected
            else:
                store =self.dbList.parent(selected)
            reply = self.mboxes(2, 2, store)
            if reply:
                children = [self.dbList.item(x)['text'] for x in self.dbList.get_children(store)]
                if self.dirtree.get_children():
                    if self.dirtree.get_children()[0] in children and not self.browsemode:
                        self.dirtree.delete(self.dirtree.get_children())
                self.dbList.delete(store)
        else:
            pass        

    def showprogress(self):
        self.status.startthread(1, 100)

    def drive_tree(self):
        self.getls = WinInfo()
        self.ls = self.getls.getdrivename()
        self.driveList.delete(*self.driveList.get_children())
        for k, v in self.ls.items():
            self.driveList.insert('', 'end', k, text=v, image=self.images['Drive'])

    def autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(first, last)

    def open_popup(self, event=None):
        top = tk.Toplevel()
        top.geometry(set_size(top, 300, 200))
        top.label = tk.Label(top, text="Hello")
        top.label.pack()
        top.entr = tk.Entry(top)
        top.entr.pack()
        top.entr.focus_set()
        top.button = tk.Button(top, text="Hello again", command=top.destroy)
        top.button.pack()
        top.transient(self.master)
        top.grab_set()
        self.master.wait_window(top)
        print(self.dirtree.item(self.dirtree.focus()))

    def additems(self, event=None):
        top = tk.Toplevel()
        top.geometry(set_size(top, 300, 100))
        top.Win = Modalwin(top)
        top.Win.pack()
        #top.Win.startthread(1, 100)
        top.Win.startthread2("D:/")
        top.protocol("WM_DELETE_WINDOW", top.Win.stop)
        top.transient(self.master)
        top.grab_set()
        self.master.wait_window(top)

    def catsettings(self, tab=0):
        '''Opens setting window'''
        Win = ExtSetting(self.master, tab)
        self.dt.read_ini()
        self.dt.update_exts()

    def toggle_cols(self):
        '''Hides or shows columns of DirTree'''
        text = ''
        if self.col2.get() == 1:
            text = text + ' ' + 'modified'
        if self.col3.get() == 1:
            text = text + ' ' + 'size'
        if self.col4.get() == 1:
            text = text + ' ' + 'type'
        if self.col5.get() == 1:
            text = text + ' ' + 'category'
        if self.col6.get() == 1:
            text = text + ' ' + 'note'
        if self.col7.get() == 1:
            text = text + ' ' + 'fullpath'
        self.dirtree.config(displaycolumns=text.strip())
        self.col_width_set()
        self.update_config()

    def read_config(self):
        self.config = ConfigParser()
        self.config.read('Config.ini')
        sec = 'Columns'
        self.col2.set(self.config.getint(sec, 'modified'))
        self.col3.set(self.config.getint(sec, 'type'))
        self.col4.set(self.config.getint(sec, 'size'))
        self.col5.set(self.config.getint(sec, 'category'))
        self.col6.set(self.config.getint(sec, 'note'))
        self.col7.set(self.config.getint(sec, 'fullpath'))
        self.toggle_cols()

    def update_config(self):
        self.config.set('Columns', 'modified', str(self.col2.get()))
        self.config.set('Columns', 'type', str(self.col3.get()))
        self.config.set('Columns', 'size', str(self.col4.get()))
        self.config.set('Columns', 'category', str(self.col5.get()))
        self.config.set('Columns', 'note', str(self.col6.get()))
        self.config.set('Columns', 'fullpath', str(self.col7.get()))
        with open('Config.ini', 'w') as configfile:
            self.config.write(configfile)

    def conmenu(self, event):
        self.tid = self.dirtree.identify_row(event.y)
        reg = self.dirtree.identify_region(event.x, event.y)
        self.colm = self.dirtree.identify_column(event.x)
        if reg == 'tree':
            if self.tid:
                self.iid = '"' + self.tid + '"'
                self.dirtree.selection_set(self.iid)
                if self.browsemode:
                    self.aMenu.post(event.x_root, event.y_root)
                else:
                    pass # add context menu containing check item existance, note editor etc
            else:
                pass
        elif reg == 'heading':
                self.headMenu.post(event.x_root, event.y_root)
                

    def open_expl(self):
        if self.tid:
            path = self.tid.replace('/', '\\')
            if os.path.isfile(self.tid):
                subprocess.Popen(["explorer", "/select,", path])
            elif os.path.isdir(self.tid):
                os.startfile(path)

    def app_quit(self):
        self.master.quit()

    def mboxes(self, mtype, m, db=None):
        if mtype == 1:
            if m==1:
                pass
            tk.messagebox.showwarning(title="Warning", message=text)
        elif mtype == 2:
            if m==1:
                text = 'Do you want to delete database "%s" ?' %(db)
                answer = tk.messagebox.askyesno(title="Deleting database", message=text)
            elif m==2:
                text = 'Do you want to close database "%s" ?' %(db)
                answer = tk.messagebox.askyesno(title="Closing database", message=text)
            return answer


########################-----class MainWindow-----###########################
#############################################################################
        
class StatusBar(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.framepro = tk.Frame(self)
        self.framepro.pack(side="left")
        self.progress = ttk.Progressbar(self.framepro, orient = tk.HORIZONTAL, length = 200) 
        self.label = tk.Label(self, bd=1, relief="sunken", anchor="e")
        self.label.pack(fill="x")
    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

    def startthread(self, mode, max=None):
        t1 = threading.Thread(target=self.pStart, args=(mode, None))
        t1.start()

    def pStart(self, mode, max=None):
        self.progress.pack()
        if mode == 1:
            self.progress.config(mode = 'determinate', maximum = max, value = 0)
            for i in range(100):
                self.progress.step()
                time.sleep(0.1)
                self.update_idletasks()
        else:
            self.progress.config(mode = 'indeterminate')
            progressbar.start()

                           
class Modalwin(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.prog = ttk.Progressbar(self, orient = tk.HORIZONTAL, length = 300)
        self.prog.grid(row=2, column=0, columnspan=2)
        self.foldername = ttk.Label(self, text="Folders:")
        self.foldername.grid(row=0, column=0, sticky="w", padx=(20, 10))
        self.foldern = ttk.Label(self)
        self.foldern.grid(row=0, column=1, sticky="e", padx=(0, 20))
        self.filename = ttk.Label(self, text="Files:")
        self.filename.grid(row=1, column=0, sticky="w", padx=(20, 10))
        self.filen = ttk.Label(self)
        self.filen.grid(row=1, column=1, sticky="e", padx=(0, 20))
        self.master = master
        self.max = 0
                           
    def setfoldernum(self, dpath):
        a=time.time()
        self.dirnum = 0
        for dirs in walk_folder(dpath):
            for dir in dirs:
                self.dirnum+=1
                self.foldern.config(text=self.dirnum)
        b=time.time()
        print(b-a)
                
    def setfilenum(self, dpath):
        time.sleep(0.5)
        self.pStart(0)
        a=time.time()
        self.dirnum = 0
        self.filenum = 0
        for dirs, files in walk_full(dpath):
            for dir in dirs:
                self.dirnum+=1
                self.foldern.config(text=self.dirnum)
            for file in files:
                self.filenum+=1
                self.filen.config(text=self.filenum)
        b=time.time()
        print(b-a)
        self.prog.stop()

    def startthread(self, mode, max=None):
        t1 = threading.Thread(target=self.pStart, args=(mode, max))
        t1.daemon = True
        t1.start()
        
    def startthread2(self, path):
        t1 = threading.Thread(target=self.setfilenum, args=(path,))
        #t2 = threading.Thread(target=self.setfilenum, args=(path,))
        t1.start()
        #t2.start()

    def pStart(self, mode, max=None):
        self.max = max
        if mode == 1:
            self.prog.config(mode = 'determinate', maximum = max, value = 0)
            while self.prog["value"]<max-1:
                self.prog.step()
                time.sleep(0.02)
            self.master.destroy()
            
                
        else:
            self.prog.config(mode = 'indeterminate')
            self.prog.start()
            
    def stop(self):
        if self.prog["mode"]=="determinate":
            self.prog.config(value=self.max-2)
            time.sleep(2)
        self.master.destroy()
        
    def pStop(self):
        self.prog.stop()
        self.progress.pack_remove()


class ModalEdit(tk.Frame):

    def __init__(self, master):
        self.cat = StringVar()
        self.values = []
        tk.Frame.__init__(self, master)
        self.foldername = ttk.Label(self, text="Folders:")
        self.foldername.grid(row=0, column=0, sticky="w", padx=(20, 10))
        self.foldern = ttk.Label(self)
        self.foldern.grid(row=0, column=1, sticky="e", padx=(0, 20))
        self.filename = ttk.Label(self, text="Files:")
        self.filename.grid(row=1, column=0, sticky="w", padx=(20, 10))
        self.filen = ttk.Label(self)
        self.filen.grid(row=1, column=1, sticky="e", padx=(0, 20))
        self.combobox = ttk.Combobox(self, textvariable = self.cat, values=values)
        self.master = master
                           
        
class WinInfo:
    def __init__(self):
        self.dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def getdrivelist(self):
        """Returns full disc drive list in Windows"""    
        self.drives = ['%s:' % d for d in self.dl if os.path.exists('%s:' % d)]
        return self.drives

    def getdrivename(self):
        self.kernel32 = ctypes.windll.kernel32
        self.volumeNameBuffer = ctypes.create_unicode_buffer(1024)
        self.fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
        self.serial_number = None
        self.max_component_length = None
        self.file_system_flags = None
        self.drivelist = self.getdrivelist()
        self.drivedict=OrderedDict()

        for drive in self.drivelist:
            self.rc = self.kernel32.GetVolumeInformationW(
                    ctypes.c_wchar_p(drive+"\\"),
                    self.volumeNameBuffer,
                    ctypes.sizeof(self.volumeNameBuffer),
                    self.serial_number,
                    self.max_component_length,
                    self.file_system_flags,
                    self.fileSystemNameBuffer,
                    ctypes.sizeof(self.fileSystemNameBuffer)
                )
            self.discname = self.volumeNameBuffer.value+" ("+drive+")"
            self.drivedict[drive+"/"] = self.discname
        return self.drivedict
        

#if __name__ == '__main__':
root = tk.Tk()
app = MainWindow(root)
root.iconbitmap('tree.ico')
root.mainloop()
