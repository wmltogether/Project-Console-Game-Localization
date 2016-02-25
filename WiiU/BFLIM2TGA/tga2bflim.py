# -*- coding: utf-8 -*-
import os,codecs,struct
from cStringIO import StringIO
import win32process,win32event
import shutil

format_dict = {"DXT1": "-bc1",
               "DXT3": "-bc2",
               "DXT5": "-bc3",
               "BC4": "-bc4",
               "BC5": "-bc5",
               "RGBA8888":"-rgb"}

def read_csv(csv_name):
    fp = open(csv_name , "rb")
    lines = fp.readlines()
    dict = {}
    for line in lines:
        if "," in line:
            (o_name, bflim_name ,width , height ,format_name , swizzle ) = line.split(",")[:-1]
            dict[bflim_name] = (o_name ,int(width) , int(height) ,format_name , int(swizzle))
    fp.close()
    return dict

def runTexconv(dds_name ,gtx_name , swizzle):
    handle = win32process.CreateProcess(u'TexConv2.exe', ' -i \"%s\" -o \"%s\" -swizzle %d'%(dds_name , gtx_name , swizzle),\
                                                    None,None,0,win32process.CREATE_NO_WINDOW,None,None,win32process.STARTUPINFO())
    win32event.WaitForSingleObject(handle[0], -1)

def runPNG2DDS(format_name ,png_name , dds_name):
    if ".tga" in png_name:
        print('nvcompress.exe -nomips %s \"%s\" \"%s\"'%(format_dict[format_name] , png_name , dds_name))
        handle = win32process.CreateProcess(u'nvcompress.exe',' -nomips %s \"%s\" \"%s\"'%(format_dict[format_name] , png_name , dds_name),\
                                                    None,None,0,win32process.CREATE_NO_WINDOW,None,None,win32process.STARTUPINFO())
        win32event.WaitForSingleObject(handle[0], -1)
    else:
        print('AMDCompressCLI.exe -fd %s \"%s\" \"%s\"'%(format_name , png_name , dds_name))
        handle = win32process.CreateProcess(u'AMDCompressCLI.exe',' -fd %s \"%s\" \"%s\"'%("ARGB8888" , png_name , dds_name),\
                                                    None,None,0,win32process.CREATE_NO_WINDOW,None,None,win32process.STARTUPINFO())
        win32event.WaitForSingleObject(handle[0], -1)

def batch_import():
    dict = read_csv("format.csv")
    fl = os.listdir("cnpng")
    for fn in fl:
        if fn[-4:].lower() in [".tga", ".png"]:
            (bflim_name ,width , height ,format_name , swizzle) = dict[fn[:-4]]
            if os.path.exists("tmp\\tmp.dds"):
                os.remove("tmp\\tmp.dds")
            if os.path.exists("tmp\\tmp.gtx"):
                os.remove("tmp\\tmp.gtx")
            runPNG2DDS(format_name ,"cnpng\\%s"%fn , "cndds\\\\%s.dds"%fn)
            runPNG2DDS(format_name ,"cnpng\\%s"%fn , "tmp\\tmp.dds")
            runTexconv("tmp\\tmp.dds" , "tmp\\tmp.gtx" , swizzle)
            fs = open("tmp\\tmp.gtx" ,"rb")
            fs.seek(0xf0)
            data_len = struct.unpack(">I" , fs.read(4))[0]
            print("%08x"%data_len)
            fs.seek(0xfc)
            dataA = fs.read(data_len)
            print("%08x"%len(dataA))
            fs.close()
            o_file = open(bflim_name , "rb")
            buffer = StringIO()
            data2 = o_file.read()
            buffer.seek(0)
            buffer.write(data2)
            o_file.close()
            buffer.seek(0)
            buffer.write(dataA)
            if not os.path.exists("REPACK\\" + "\\".join(("%s"%(bflim_name)).split("\\")[1:-1])):
                os.makedirs("REPACK\\" + "\\".join(("%s"%(bflim_name)).split("\\")[1:-1]))
            dest = open("REPACK\\" + "\\".join(("%s"%(bflim_name)).split("\\")[1:]) , "wb")
            dest.write(buffer.getvalue())
            dest.close()
            buffer.flush()


batch_import()