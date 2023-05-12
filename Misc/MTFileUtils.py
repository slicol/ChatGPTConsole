# Copyright 1998-2022 Tencent Games, Inc. All Rights Reserved.
#                            
# 一些常用的File处理函数
#@Slicol

import hashlib
import logging
import os
from zipfile import ZipFile
import zipfile
import csv

from Misc.MTStringUtils import StringEndswith

########################################################################
def FindFileByKeyword(dir:str, keyword:str, ext:str, recursive:bool)->str:
    if(recursive == True):
        for foldername, subfolders, filenames in os.walk(dir):
            if len(filenames) < 1: continue
            for item in filenames:
                if(item.find(keyword) >= 0):
                    if ext != "" or ext != None:
                        if item.endswith(ext):
                            return os.path.join(foldername, item)
                        pass
                    else:
                        return os.path.join(foldername, item)
                    pass
                pass
            pass
        pass
    else:
        items = os.listdir(dir)
        for item in items:
            fullpath = os.path.join(dir, item) 
            if(os.path.isfile(fullpath)):
                if(item.find(keyword) >= 0):
                    if ext != "" or ext != None:
                        if item.endswith(ext):
                            return fullpath
                        pass
                    else:
                        return fullpath
                    pass
                pass
            pass
        pass
    pass
    return ""

########################################################################
def FindFolderByKeyword(dir:str, keyword:str, recursive:bool)->str:
    if(recursive == True):
        for foldername, subfolders, filenames in os.walk(dir):
            if len(subfolders) < 1: continue
            for item in subfolders:
                if(item.find(keyword) >= 0):
                    return os.path.join(foldername, item)
                pass
            pass
        pass
    else:
        items = os.listdir(dir)
        for item in items:
            fullpath = os.path.join(dir, item) 
            if(os.path.isdir(fullpath)):
                if(item.find(keyword) >= 0):
                    return fullpath
                pass
            pass
        pass
    pass
    return ""

########################################################################
def ZipDir(dir:str, zipname:str):
    with ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as zipobj:
        for foldername, subfolders, filenames in os.walk(dir):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                relpath = os.path.relpath(filepath, dir)
                zipobj.write(filepath, relpath)
            pass
        pass
    pass

########################################################################
def UnZip(outdir:str, srcfile:str):
    with ZipFile(srcfile, 'r', zipfile.ZIP_DEFLATED) as zipobj:
        zipobj.extractall(outdir)
    pass


########################################################################
def ToSizeString(size):
    if size < 1024:
        return '%dByte' % (size)
    elif size < 1024 * 1024:
        return '%0.2fKB' % (size/1024)
    elif size < 1024*1024*1024:
        return '%0.2fMB' % (size/(1024*1024))
    else:
        return '%0.2fGB' % (size/(1024*1024*1024)) 
    pass

########################################################################
def GetFileMD5(filepath:str):
    m = hashlib.md5()
    with open(filepath,'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            pass
            m.update(data)
        pass
    pass
    return m.hexdigest()


########################################################################
def GetFileSize(filepath:str):
    size = os.path.getsize(filepath)
    return size

########################################################################
def GetAllEmptyDirs(dirpath:str):
    items = os.listdir(dirpath)
    result = []
    if len(items) == 0:
        result.append(dirpath)
        return result
    pass

    for item in items:
        fullpath = dirpath + "/" + item
        if os.path.isdir(fullpath):
            tmp = GetAllEmptyDirs(fullpath)
            if len(tmp) > 0:
                result.extend(tmp)
            pass
        pass
    pass
    
    return result
    

########################################################################
def RemoveAllEmptySubDirs(basedir:str, _test=False):
    items = GetAllEmptyDirs(basedir)
    if len(items) == 1 and items[0] == basedir: return
    
    lockfile = basedir + "RemoveAllEmptySubDirs.lock"
    f_lock = open(lockfile, "w")
    f_lock.write("")
    f_lock.close()

    for item in items:
        logging.info("Remove Dirs: %s", item)
        if not _test:
            os.removedirs(item)
        pass
    pass

    os.remove(lockfile)
    pass

########################################################################
def GetAllFiles(dirpath:str, _extnames = "",_mtimescope = [])->list:
    files = os.listdir(dirpath)
    result = []
    extnames = []
    if isinstance(_extnames, list):
        extnames = _extnames
    else:
        extnames = _extnames.split("|")
    pass

    bValidModifyTimeScope = len(_mtimescope) == 2
    mtime_min = 0
    mtime_max = 0
    if bValidModifyTimeScope:
        mtime_min = _mtimescope[0]
        mtime_max = _mtimescope[1]
    pass

    for file in files:
        filepath = dirpath + "/" + file

        if not os.path.isdir(filepath):
            if StringEndswith(filepath, extnames) :
                if bValidModifyTimeScope:
                    st = os.stat(filepath)
                    if st.st_mtime >= mtime_min and st.st_mtime <= mtime_max:
                        result.append(filepath)
                    pass
                else:
                    result.append(filepath)
                pass
            pass
        else:
            tmp = GetAllFiles(filepath, extnames, _mtimescope)
            result.extend(tmp)
        pass
    pass
    return result    


########################################################################
def GetAllLines(filepath:str):
    lines = []
    f = None
    try:
        f = open(filepath,"r",encoding="UTF-8")
        lines = f.readlines()
        f.close()
    except Exception as e:
        if f != None: f.close()

        try:
            f = open(filepath, "r")
            lines = f.readlines()
            f.close()
        except Exception as e:
            if f != None: f.close()
            
            logging.error("GetAllLines: %s", filepath)
            logging.error(e)
            lines = []
        pass
    pass
    return lines

########################################################################
def MakeSureParentDir(path:str):
    i = path.rfind('/')
    if i < 0: i = path.rfind('\\')
    if i >= 0: path = path[0:i]
    if not os.path.exists(path):
        os.makedirs(path)
    pass

########################################################################
def MakeSureDir(path:str):
    if not os.path.exists(path):
        os.makedirs(path)
    pass
########################################################################
def LoadCSVFile(path:str):
    rows = []
    with open(path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rows.append(row)
    return rows

########################################################################
def ReadText(fileName):
    f = open(fileName, 'r',encoding="utf-8")
    text = f.read()
    f.close()
    return text

def ReadTextUtf8Sig(fileName):
    f = open(fileName, 'r',encoding="utf-8-sig")
    text = f.read()
    f.close()
    return text    

########################################################################
def AppendText(filepath:str, text:str):
    f = open(filepath, 'a',encoding="utf-8")
    f.write(text)
    f.close()

########################################################################
def SaveText(filepath:str, text:str):
    f = open(filepath, 'w',encoding="utf-8")
    f.write(text)
    f.close()