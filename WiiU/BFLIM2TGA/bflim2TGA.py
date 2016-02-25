# -*- coding: utf-8 -*-
import os,codecs,struct
from cStringIO import StringIO
import win32process,win32event
import shutil
def runTexconv(filename):
    handle = win32process.CreateProcess(u'TexConv2.exe','-i %s -o \"tmp\\tmp.dds\"'%(r'"'+filename+r'"'),\
                                                    None,None,0,win32process.CREATE_NO_WINDOW,None,None,win32process.STARTUPINFO())
    win32event.WaitForSingleObject(handle[0], -1)

def runDDS2PNG(filename ,format_name):
    if format_name == "RGBA8888":
        dds_name = r'"'+filename+r'"'
        png_name = r'"'+filename[:-4] + '.png'+r'"'
        handle = win32process.CreateProcess(u'AMDCompressCLI.exe',' %s %s'%(dds_name , png_name),\
                                                    None,None,0,win32process.CREATE_NO_WINDOW,None,None,win32process.STARTUPINFO())
        win32event.WaitForSingleObject(handle[0], -1)
    else:
        
        handle = win32process.CreateProcess(u'nvdecompress.exe',' %s'%(r'"'+filename+r'"'),\
                                                    None,None,0,win32process.CREATE_NO_WINDOW,None,None,win32process.STARTUPINFO())
        win32event.WaitForSingleObject(handle[0], -1)

def dir_fn(adr ,ext_name):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            ext = name.split('.')[-1]
            adrlist=os.path.join(root, name)
            if ext.lower() in ext_name:
                dirlst.append(adrlist)
    return dirlst
DDS_header = "\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x00\x04\x00\x00" + \
             "\x00\x04\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x01\x00\x00\x00" + \
             "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + \
             "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + \
             "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00" + \
             "\x04\x00\x00\x00\x41\x54\x49\x31\x00\x00\x00\x00\x00\x00\x00\x00" + \
             "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00" + \
             "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
GTX_header = "\x47\x66\x78\x32\x00\x00\x00\x20\x00\x00\x00\x07\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x0B\x00\x00\x00\x9C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x34\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x0D\x03\x00\x00\x00\x20\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x02\x03\x03\xF8\x0F\x21\xCC\x00\x00\x7F\x06\x88\x80\x00\x00\x00\x00\x00\x80\x00\x00\xF0\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x0C\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00"
GTX_header = "\x47\x66\x78\x32\x00\x00\x00\x20\x00\x00\x00\x07\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x0B\x00\x00\x00\x9C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x33\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x0D\x03\x00\x00\x00\x20\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x02\x03\x03\xF8\x0F\x21\xCC\x00\x00\x7F\x06\x88\x80\x00\x00\x00\x00\x00\x80\x00\x00\xF0\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x0C\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00"
GTX_end = "\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"



def bflim2gtx(name , csv_buffer):
    fp = open(name , "rb")
    fp.seek(-0x28,2)
    sig = fp.read(4)
    endian  = fp.read(2)
    null = fp.read(2)
    allSize = struct.unpack(">I" ,fp.read(4))[0]
    fp.seek(-0xc,2)
    WIDTH = struct.unpack(">H" ,fp.read(2))[0]
    HEIGHT = struct.unpack(">H" ,fp.read(2))[0]
    unk = struct.unpack(">H" ,fp.read(2))[0]
    FORMAT = ord(fp.read(1))
    SWIZZLE = ord(fp.read(1))
    if SWIZZLE == 2:
        SWIZZLE = 4
    FLIMSIZE = struct.unpack(">I" ,fp.read(4))[0]
    fp.seek(0,0)
    DATA = fp.read(FLIMSIZE)
    SWIZZLE = (SWIZZLE - 4 )/ 0x20
    formatName= {0x8:"RGB565",
                 0x1a:"RGBA8888",
                 0x31:"DXT1",
                 0x32:"DXT3",
                 0x33:"DXT5",
                 0x34:"BC4",
                 0x35:"BC5"}
    TMP = {0x5:0x8,
           0x9:0x1a,
           0xc:0x31,
           0xd:0x32,
           0xe:0x33,
           0xf:0x34,
           0x10:0x34,
           0x11:0x35,
           0x14:0x1a,
           0x15:0x31,
           0x16:0x32,
           0x17:0x33}

    dest = open("gtx\\%s.gtx"%(name.replace("\\" , "__")), "wb")
    dest.write(GTX_header)
    dest.write(DATA)
    dest.write(GTX_end)

    if FORMAT in TMP:
        FORMAT = TMP[FORMAT]
    else:
        print("Error FORMAT:%X"%FORMAT)
        return ""
    dest.seek(0x46)
    dest.write(struct.pack(">H" , WIDTH))
    dest.seek(0x7E)
    dest.write(struct.pack(">H" , WIDTH))
    dest.seek(0x4A)
    dest.write(struct.pack(">H" , HEIGHT))
    dest.seek(0x60)
    dest.write(struct.pack(">I" , FLIMSIZE))
    dest.seek(0xF0)
    dest.write(struct.pack(">I" , FLIMSIZE))
    dest.seek(0x57)
    dest.write(chr(FORMAT))
    dest.seek(0x76)
    dest.write(chr(SWIZZLE))
    dest.close()
    csv_buffer.write("%s,%s,%d,%d,%s,%d,\r\n"%(name , name.replace("\\" , "__") ,
                                               WIDTH , HEIGHT , formatName[FORMAT] , SWIZZLE))
    fp.close()
    return formatName[FORMAT]

def getBFLIM():
    fl = dir_fn("UNPACK" , ["bflim"])
    csv_buffer = open("format.csv" , "wb")
    for fn in fl:
        print(fn)
        formatName = bflim2gtx(fn ,csv_buffer)
        gtx_name = "gtx\\%s.gtx"%(fn.replace("\\" , "__"))
        if os.path.exists(gtx_name):
            runTexconv(gtx_name)
            if os.path.exists("tmp\\tmp.dds"):
                runDDS2PNG("tmp\\tmp.dds" ,formatName)
                if os.path.exists("tmp\\tmp.tga"):
                    shutil.copyfile("tmp\\tmp.tga" , "png\\%s.tga"%(fn.replace("\\" , "__")))
                    os.remove("tmp\\tmp.tga")
                    os.remove("tmp\\tmp.dds")
                if os.path.exists("tmp\\tmp.png"):
                    shutil.copyfile("tmp\\tmp.png" , "png\\%s.png"%(fn.replace("\\" , "__")))
                    os.remove("tmp\\tmp.png")
                    os.remove("tmp\\tmp.dds")


getBFLIM()





