##############################################################################
##                              File operations                             ##
##############################################################################
import os
import time
import tkinter as tk
import pandas as pd
from configparser import ConfigParser

def file_ext(path):
    try:
        if os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext:
                return ext
            else:
                return ''
        else:
            return ''
    except Exception as err:
        print('In file_ext ', err)
        return False
    
def file_type(path):
    #finish this!!!!!
    try:
        if os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext:
                pass
    except:
        pass
    

def file_attr(p, dir=False):
    try:
        mdate = time.strftime('%d.%m.%Y %H:%M', time.localtime(os.path.getmtime(p)))
    except Exception as er:
        #print('In file_attr mdate', er)
        mdate = ""
    if not dir:
        try:
            size = os.stat(p).st_size
        except:
            size = None    
        #ext = file_ext(p)
    else:
        size = None
    #imgname = "self.img" + ptype.replace(" file", "")
    return mdate, size

        
    tree.item(id, image=self.imgMisc)
    if (numrow % 2 == 0): tree.item(id, tags=("even",))
    numrow += 1    

    
def get_exts():
    file = 'Config.ini'
    config = ConfigParser()
    config.read(file)
    extdic = dict(config.items('File extensions'))
    return extdic

def check_extfile():
    '''check file extension'''
    file = 'Config.ini'
    if not os.path.isfile(file) or os.stat(file).st_size == 0:
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(fileext())   

def open_store(name, new=False):
    store = pd.HDFStore(name, format='f', mode='a', complib='zlib', complevel=9)
    return store


def get_imgs(path): 
    '''Gets dictionary containing icons'''
    imgcache = { os.path.splitext(filename)[0] : tk.PhotoImage(
            file = os.path.join(path, filename)) for filename in os.listdir(path) }
    return imgcache

def month_name(n):
    month = {
    1:'January', 2:'February',
    3:'March', 4:'April',
    5:'May', 6:'June',
    7:'July', 8:'August',
    9:'September', 10:'October',
    11:'November', 12:'December'
    }
    return month[n]

#Customized os.walk function
def walk_folder(top, topdown=True, onerror=None, followlinks=False):
    dirs = []
    try:
        scandir_it = os.scandir(top)
        entries = list(scandir_it)
    except OSError as error:
        if onerror is not None:
            onerror(error)
        return

    for entry in entries:
        try:
            is_dir = entry.is_dir()
        except OSError:
            # If is_dir() raises an OSError, consider that the entry is not
            # a directory, same behaviour than os.path.isdir().
            is_dir = False

        if is_dir:
            dirs.append(entry.name)

    if topdown:
        yield dirs

        # Recurse into sub-directories
        islink, join = os.path.islink, os.path.join
        for dirname in dirs:
            new_path = join(top, dirname)
            # Issue #23605: os.path.islink() is used instead of caching
            # entry.is_symlink() result during the loop on os.scandir() because
            # the caller can replace the directory entry during the "yield"
            # above.
            if followlinks or not islink(new_path):
                yield from walk_folder(new_path, topdown, onerror, followlinks)
    else:
        # Yield after recursion if going bottom up
        yield dirs

def walk_file(top, topdown=True, onerror=None, followlinks=False):
    dirs = []
    nondirs = []
    try:
        scandir_it = os.scandir(top)
        entries = list(scandir_it)
    except OSError as error:
        if onerror is not None:
            onerror(error)
        return

    for entry in entries:
        try:
            is_dir = entry.is_dir()
        except OSError:
            # If is_dir() raises an OSError, consider that the entry is not
            # a directory, same behaviour than os.path.isdir().
            is_dir = False

        if is_dir:
            dirs.append(entry.name)
        else:
            nondirs.append(entry.name)

    yield nondirs
    # Recurse into sub-directories
    join = os.path.join
    for dirname in dirs:
        new_path = join(top, dirname)
        yield from walk_file(new_path, topdown, onerror, followlinks)


def walk_full(top, known=[], hidden=False, skip=[], followlinks=False):
    dirs = []
    nondirs = []
    try:
        scandir_it = os.scandir(top)
        entries = list(scandir_it)
    except OSError as error:
        return

    for entry in entries:
        try:
            is_dir = entry.is_dir()
        except OSError:
            is_dir = False

        if skip and entry.name not in skip:
            if is_dir:
                dirs.append(entry.name)
            else:
                ext = os.path.splitext(entry.name)[1]
                if known and  ext in known:
                    nondirs.append(entry.name)
                elif not known:
                    nondirs.append(entry.name)
        elif not skip:
            if is_dir:
                dirs.append(entry.name)
            else:
                if known and entry.name not in known:
                    nondirs.append(entry.name)
                elif not known:
                    nondirs.append(entry.name)

    yield top, dirs, nondirs

    # Recurse into sub-directories
    islink, join = os.path.islink, os.path.join
    for dirname in dirs:
        new_path = join(top, dirname)
        yield from walk_full(new_path, known, hidden, skip, followlinks)

def fileext():
    fileexts = '''[Skipped items]
showhiddenitems = 1
showonlyknownitems = 1
skiplisteditems = 1

[SkippedList]

[File extensions]
.3dm:CAD file
.3ds:CAD file
.3g2:Video file
.3ga:Audio file
.3gp:Video file
.3gpp:Video file
.7z:Archive file
.aac:Audio file
.accdb:Database file
.ai:Misc file
.aif:Audio file
.aifc:Audio file
.aiff:Audio file
.amr:Audio file
.apk:Archive file
.app:Misc file
.art:Image file
.arw:Image file
.asf:Video file
.asp:Website file
.aspx:Website file
.au:Audio file
.aup:Audio file
.avi:Video file
.azw:eBook file
.azw3:eBook file
.bat:Misc file
.bin:Misc file
.bmp:Image file
.bup:Database file
.bz2:Archive file
.c:Website file
.cab:Archive file
.caf:Audio file
.cbr:eBook file
.cda:Misc file
.cdr:Misc file
.cer:Website file
.cfg:Misc file
.cfm:Website file
.cgi:Misc file
.chm:Document file
.class:Misc file
.com:Misc file
.cpi:Video file
.cpl:Misc file
.cpp:Misc file
.cr2:Image file
.crdownload:Misc file
.crw:Image file
.crx:Archive file
.cs:Misc file
.csr:Website file
.css:Website file
.csv:Spreadsheet file
.dat:Misc file
.db:Database file
.dcm:Image file
.dds:Image file
.deb:Archive file
.dem:Misc file
.deskthemepack:Misc file
.divx:Video file
.djvu:Image file
.dll:Misc file
.dmg:Image file
.dmp:Misc file
.dng:Image file
.doc:Document file
.docm:Document file
.docx:Document file
.dot:Document file
.dotx:Document file
.drv:Misc file
.dtd:Misc file
.dwg:CAD file
.dxf:CAD file
.eml:Document file
.emz:Misc file
.eps:Misc file
.epub:eBook file
.exe:Application
.exr:Image file
.f4v:Video file
.fb2:eBook file
.fla:Misc file
.flac:Audio file
.flv:Video file
.fnt:Misc file
.fon:Misc file
.fpx:Image file
.gadget:Misc file
.gam:Misc file
.ged:Database file
.gif:Image file
.gpx:Misc file
.gsm:Audio file
.gz:Archive file
.gzip:Archive file
.h:Misc file
.h264:Video file
.hdr:Image file
.htm:Website file
.html:Website file
.hwp:Document file
.icns:Image file
.ico:Image file
.ics:Misc file
.iff:Audio file
.ifo:Video file
.img:Misc file
.indd:Misc file
.inf:Misc file
.ini:Misc file
.ipa:Misc file
.iso:Misc file
.ithmb:Image file
.itl:Database file
.jad:Misc file
.jar:Archive file
.java:Misc file
.jp2:Image file
.jpeg:Image file
.jpg:Image file
.js:Website file
.json:Website file
.jsp:Website file
.kar:Audio file
.key:Presentation file
.keychain:Misc file
.kml:Misc file
.kmz:Misc file
.lit:eBook file
.lnk:Misc file
.log:Document file
.lrf:eBook file
.lua:Misc file
.m:Misc file
.m2ts:Video file
.m3u:Document file
.m4a:Audio file
.m4p:Audio file
.m4r:Audio file
.m4v:Video file
.max:CAD file
.mbp:eBook file
.mdb:Database file
.mdf:Misc file
.mdi:Misc file
.mid:Audio file
.midi:Audio file
.mim:Misc file
.mkv:Video file
.mmf:Audio file
.mobi:eBook file
.mod:Video file
.mov:Video file
.mp2:Audio file
.mp3:Audio file
.mp4:Video file
.mpa:Audio file
.mpeg:Video file
.mpg:Video file
.mpga:Audio file
.msg:Document file
.msi:Application
.mswmm:Video file
.mts:Video file
.mxf:Video file
.nef:Image file
.nes:Misc file
.nfo:Misc file
.nrw:Image file
.obj:CAD file
.odg:Misc file
.odp:Presentation file
.ods:Spreadsheet file
.odt:Document file
.ogg:Audio file
.ogv:Video file
.oma:Audio file
.opf:eBook file
.opus:Audio file
.orf:Image file
.otf:Misc file
.oxps:Document file
.pages:Document file
.pcd:Image file
.pcx:Image file
.pdb:Database file
.pdf:Document file
.pes:Misc file
.php:Website file
.pict:Image file
.pif:Misc file
.pkg:Misc file
.pl:Misc file
.plugin:Misc file
.png:Image file
.pps:Presentation file
.ppsx:Presentation file
.ppt:Presentation file
.pptm:Presentation file
.pptx:Presentation file
.prc:eBook file
.ps:Misc file
.psd:Image file
.pspimage:Image file
.pub:Document file
.py:Misc file
.qcp:Audio file
.qt:Video file
.ra:Audio file
.ram:Audio file
.rar:Archive file
.rem:Misc file
.rm:Video file
.rom:Misc file
.rpm:Archive file
.rss:Website file
.rtf:Document file
.sav:Misc file
.sdf:Database file
.sfw:Image file
.sh:Misc file
.sitx:Archive file
.sln:Misc file
.sql:Database file
.srt:Video file
.svg:Misc file
.swf:Video file
.swift:Misc file
.sxw:Document file
.sys:Misc file
.tar:Archive file
.tar.gz:Archive file
.tax2014:Misc file
.tcr:eBook file
.tex:Document file
.tga:Image file
.tgz:Archive file
.thm:Image file
.tif:Image file
.tiff:Image file
.toast:Misc file
.torrent:Misc file
.ts:Video file
.ttf:Misc file
.txt:Document file
.uue:Misc file
.vb:Misc file
.vcd:Misc file
.vcf:Misc file
.vcxproj:Misc file
.vep:Video file
.vob:Video file
.vsd:Misc file
.wav:Audio file
.wbmp:Image file
.webm:Video file
.webp:Image file
.wlmp:Video file
.wma:Audio file
.wmf:Misc file
.wmv:Video file
.wpd:Document file
.wpg:Misc file
.wps:Document file
.wsf:Misc file
.xcf:Image file
.xcodeproj:Misc file
.xls:Spreadsheet file
.xlsx:Spreadsheet file
.xml:Document file
.xps:Document file
.xspf:Audio file
.yuv:Image file
.zip:Archive file
.zipx:Archive file'''
    return fileexts
