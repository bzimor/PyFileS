###############################################################################
##                              Tree manipulations                           ##
###############################################################################
import os
import stat
import time
from os.path import join, isdir
from configparser import ConfigParser
import pandas as pd
import Filesio as fio

class DirTree:
    def __init__(self):
        self.toggle = True
        self.cdir = os.path.abspath('.').replace('\\', '/')
        self.theme = 'win7'
        self.iconpath = self.cdir + '/img/' + self.theme + '/'
        self.images = fio.get_imgs(self.iconpath)
        self.read_ini()
        self.update_exts()
        

    def read_ini(self):
        '''Opens and reads ini file to get settings below'''
        self.ignorelist = []
        self.config = ConfigParser()
        self.config.read('Config.ini')
        sect = 'Skipped items'
        self.known = self.config.getint(sect, 'ShowOnlyKnownItems')
        self.hidden = self.config.getint(sect, 'ShowHiddenItems')
        self.skipped = self.config.getint(sect, 'SkipListedItems')
        for item in self.config.items('SkippedList'):
            self.ignorelist.append(item[1])

    def update_exts(self):
        '''Update file extension dictionary'''
        self.extdic = fio.get_exts()

    def is_hidden(self, filepath):
        '''Returns file hidden status in Windows'''    
        return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
        
    def populate_roots(self, tree, dirname):
        if dirname:
            dirname = dirname.replace('\\', '/')
            tree.delete(*tree.get_children())
            self.node = tree.insert('', 'end', dirname, text=dirname, image = self.images["Drive"], 
                                    values=[dirname, "Folder"], tags=("even",))
            tree.item(self.node, open=True)
            self.populate_tree(tree, self.node)


    def populate_tree(self, tree, node):
        if tree.set(node, "type") != 'Folder':
            return
        path = tree.set(node, "fullpath")
        tree.delete(*tree.get_children(node))
        numrow = 1
        if self.skipped:
            l = [(isdir(os.path.join(path, name)), name) for name in \
                os.listdir(path) if name not in self.ignorelist]
        else:
            l = [(isdir(os.path.join(path, name)), name) for name in os.listdir(path)]
        l.sort(reverse=True, key=lambda item: item[0])
        for item in l:
            ptype = None
            p = os.path.join(path, item[1]).replace('\\', '/')
            pext = fio.file_ext(p)
            if self.known:
                if pext in self.extdic:
                    ptype = self.extdic[pext]
                elif pext == '':
                    ptype = 'Folder'
                else:
                    continue
                id = tree.insert(node, "end", p, text=item[1], values=[p, ptype])
                if ptype == 'Folder':
                    try:
                        if len(list(os.listdir(p)))>0:
                            tree.insert(id, 0, text="dummy")
                    except:
                        pass
                    tree.item(id, text=item[1], image=self.images[ptype])    
                    attr = fio.file_attr(p, True)
                    tree.set(id, "modified", attr[0])
                    if (numrow % 2 == 0): tree.item(id, tags=("even",))
                    numrow += 1
                else:
                    attr = fio.file_attr(p)
                    filesize = "{:,}".format(attr[1]).replace(",", " ") + ' kb'
                    tree.set(id, "size", filesize)
                    tree.set(id, "modified", attr[0])
                    if pext in self.images:
                        tree.item(id, image=self.images[pext])
                    else: tree.item(id, image=self.images[ptype])
                    if (numrow % 2 == 0): tree.item(id, tags=("even",))
                    numrow += 1
            else:
                if pext in self.extdic:
                    ptype = self.extdic[pext]
                elif pext == None:
                    ptype = 'Folder'
                else:
                    ptype = 'File'
                id = tree.insert(node, "end", p, text=item[1], values=[p, ptype])
                if ptype == 'Folder':
                    try:
                        if len(list(os.listdir(p)))>0:
                            tree.insert(id, 0, text="dummy")
                    except:
                        pass
                    tree.item(id, text=item[1], image=self.images[ptype])    
                    attr = fio.file_attr(p, True)
                    tree.set(id, "modified", attr[0])
                    if (numrow % 2 == 0): tree.item(id, tags=("even",))
                    numrow += 1
                else:
                    attr = fio.file_attr(p)
                    filesize = "{:,}".format(attr[1]).replace(",", " ")
                    tree.set(id, "size", filesize)
                    tree.set(id, "modified", attr[0])
                    if pext in self.images:
                        tree.item(id, image=self.images[pext])
                    else: tree.item(id, image=self.images[ptype])
                    if (numrow % 2 == 0): tree.item(id, tags=("even",))
                    numrow += 1
        
        
    def buildtree(self, tree, node, store):
        d=time.time()
        mydata = store.select(node)
        tree.delete(*tree.get_children())
        if node.endswith(':'):
            node = node + '/'
        tree.insert("", "end", node, text=node, image=self.images['Drive'], open=True, values=[node, "Local drive"])
        for rows in mydata.itertuples():
            ID = rows[0]
            parent = os.path.split(ID)[0]
            text = os.path.split(ID)[1]
            type = rows[3]
            modified = rows[2]
            filesize = int(rows[1]/1024)
            filesize = "{:,}".format(filesize).replace(",", " ")
            tree.insert(parent, "end", ID, text=text, values=[ID, type, filesize, modified])
            if type == 'Folder':
                tree.item(ID, image=self.images['Folder'])
            else:
                ext = fio.file_ext(ID)
                if ext in self.images:
                    tree.item(ID, image=self.images[ext])
                else:
                    tree.item(ID, image=self.images[type])
            #temp.append(text)
        c=time.time()-d
        store.close()
        print(c)

    def buildtree_cat(self, tree, node, store):
        d=time.time()
        mydata = store.select(node)
        tree.delete(*tree.get_children())
        filecats = sorted(list(set(list(self.extdic.values()))))
        filetypes = sorted([item.replace('.', '') for item in list(self.extdic.keys())])
        for item in filecats:
            tree.insert("", "end", item, image=self.images[item], text=item)
        for item in filetypes:
            if item:
                tree.insert(self.extdic['.'+item], "end", item, text=item)
            else: continue
        for rows in mydata.itertuples():
            ID = rows[0]
            ext = fio.file_ext(ID)
            parent = ext.replace('.', '')
            text = os.path.split(ID)[1]
            type = rows[3]
            modified = rows[2]
            filesize = int(rows[1]/1024)
            filesize = "{:,}".format(filesize).replace(",", " ")
            if parent in filetypes:
                tag = self.tagtoggle()
                tree.insert(parent, "end", ID, text=text, tags=(tag,), values=[ID, type, filesize, modified])
                if ext in self.images:
                    tree.item(ID, image=self.images[ext])
                else:
                    tree.item(ID, image=self.images[type])
            else: continue
        for n in filecats:
            for child in tree.get_children(n):
                if not len(tree.get_children(child)):
                    tree.delete(child)
            if not len(tree.get_children(n)):
                tree.delete(n)
        c=time.time()-d
        store.close()
        print(c)

    def buildtree_date(self, tree, node, store):
        d=time.time()
        mydata = store.select(node)
        mydata = mydata.sort_values(['modified'])
        tree.delete(*tree.get_children())
        years = sorted(list(set(list(mydata['modified'].dt.year))))
        pairs = sorted(list(set(zip(mydata['modified'].dt.month, mydata['modified'].dt.year))))
        for item in years:
            tree.insert("", "end", item, image=self.images['Folder'], text=item)
        for m, y in pairs:
            tree.insert(y, "end", str(m)+str(y), image=self.images['Folder'], text=fio.month_name(m))
        for rows in mydata.itertuples():
            ID = rows[0]
            ext = fio.file_ext(ID)
            parent = str(rows[2].month) + str(rows[2].year)
            text = os.path.split(ID)[1]
            type = rows[3]
            modified = rows[2]
            filesize = int(rows[1]/1024)
            filesize = "{:,}".format(filesize).replace(",", " ")
            tag = self.tagtoggle()
            if type != "Folder":
                tree.insert(parent, "end", ID, text=text, tags=(tag,), values=[ID, type, filesize, modified])
                if ext in self.images:
                    tree.item(ID, image=self.images[ext])
                else:
                    tree.item(ID, image=self.images[type])
        c=time.time()-d
        store.close()
        print(c)

    def gettree(self, path, store):
        a=time.time()
        id=[]
        type=[]
        modified=[]
        filesize=[]
        for root, dirs, files in fio.walk_full(path, self.extdic, self.hidden, self.ignorelist):
        #for root, dirs, files in os.walk(path):
            dirs.sort()
            files.sort()
            for dir in dirs:
                did = join(root, dir).replace("\\", "/")
                attr = fio.file_attr(did, True)
                id.append(did)
                type.append("Folder")
                modified.append(attr[0])
                filesize.append(0)
            for file in files:
                fid = join(root, file).replace("\\", "/")
                attr = fio.file_attr(fid)
                ftype = self.extdic[fio.file_ext(fid)]
                id.append(fid)
                type.append(ftype)
                modified.append(attr[0])
                filesize.append(attr[1])
        df = pd.DataFrame({'type':type, 'modified':modified, 'filesize':filesize}, index=id)
        df['modified'] = pd.to_datetime(df['modified'], dayfirst=True)
        store[path] = df
        b=time.time()
        store.close()
        print(b-a) 

    def database_items(self, dbpath, tree, store, rebuild=False):
        if dbpath not in tree.get_children() or rebuild:
            if dbpath not in tree.get_children():
                node = tree.insert('', 'end', dbpath, image=self.images['DBsaved'], text=dbpath)
                tree.item(dbpath, open=True)
            else:
                node = dbpath
                tree.delete(*tree.get_children(node))
            for item in list(store):
                #item = item.replace('/', '')
                item = item[1:]
                tree.insert(node, 'end', node+item, text=item)
                if len(item)<3:
                    tree.item(node+item, image=self.images['Drive'])
                else:
                    tree.item(node+item, image=self.images['Folder'])
            store.close()
        else:
            tree.selection_set('"'+dbpath+'"')

    def savetreecsv(self, node):
        a=time.time()
        mydata = open("D:/Dirtree.csv", "w", encoding="utf-8")
        fieldnames = ["id", "parent", "text", "type", "modified", "filesize"]
        writer = csv.DictWriter(mydata, fieldnames=fieldnames, delimiter="|")
        for root, dirs, files in os.walk(node):
            dirs =sorted(dirs)
            files = sorted(files)
            for dir in dirs:
                did = join(root, dir).replace("\\", "/")
                try:
                    mdate = time.strftime('%d.%m.%Y %H:%M', time.localtime(os.path.getmtime(did)))
                except Exception as er:
                    #print(er)
                    mdate = "Access denied"
                dparent = root.replace("\\", "/")
                writer.writerow({"id":did, "parent":dparent, "text":dir, "type":"Folder",
                                 "modified":mdate, "filesize":""})
                #pickle.dump(entry, mydata)
            for file in files:
                fid = join(root, file).replace("\\", "/")
                try:
                    mdate = time.strftime('%d.%m.%Y %H:%M', time.localtime(os.path.getmtime(fid)))
                except Exception as er:
                    mdate = "Access denied"
                try:
                    size = int((os.stat(fid).st_size)/1024)
                    size = "{:,}".format(size).replace(",", " ")
                except:
                    size="Unknown"
                fparent = root.replace("\\", "/")
                #ftype = file_type(fid)
                ext = os.path.splitext(fid)[1].lower()
                writer.writerow({"id":fid, "parent":dparent, "text":file, "type":ext,
                                 "modified":mdate, "filesize":size})
                #pickle.dump(entry, mydata)
        b=time.time()
        mydata.close()
        print(b-a)

    def readtreecsv(self, tree, event=None):
        a=time.time()
        node="G:/"
        tree.delete(*self.dirtree.get_children())
        tree.insert("", "end", node, text=node, values=[node, "Folder"])
        with open('D:/Dirtree.csv', encoding="utf-8") as csvfile:
            fieldnames = ["id", "parent", "text", "type", "modified", "filesize"]
            reader = csv.DictReader(csvfile, fieldnames = fieldnames, delimiter="|")
            for row in reader:
                tree.insert(row["parent"], "end", row["id"], text=row["text"], tags=(row["type"],), values=[row["id"], row["type"], row["filesize"], row["modified"]])
        b=time.time()
        print(b-a)
    
    def tagtoggle(self):
        if self.toggle:
            self.toggle = False
            txt = "odd"
        else:
            self.toggle = True
            txt = "even"
        return txt     
    
    def getnum(self, dpath):
        self.dirnum = 0
        self.filenum = 0
        a=time.time()
        for root, dirs, files in os.walk(dpath):
            for dir in dirs:
                self.dirnum+=1
                Modal.setfoldernum(self.dirnum)
            for file in files:
                self.filenum+=1
                Modal.setfoldernum(self.filenum)
        b=time.time()
        print(b-a)
        print(self.dirnum+self.filenum)
