import codecs,struct,os
from glob import iglob
from nlzss import *
import struct
from cStringIO import StringIO
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def readUString(buffer,blen):
    data = ""
    string = u""
    while True:
        if (buffer.tell() + 1 >= blen):
            break
        fbyte= buffer.read(1)
        sbyte = buffer.read(1)
        if (ord(fbyte),ord(sbyte)) == (0,0):
            break
        data = (fbyte + sbyte)
        tmp, = struct.unpack(">H" , data)
        if tmp == 0xe:
            b,c,d = struct.unpack(">3H" , buffer.read(6))
            tmp = ""
            if d == 0:
                tmp += ("{0E:%x:%x:%x}"%(b,c,d)).upper()
            else:
                var = struct.unpack(">%dH"%(d/2) , buffer.read(d))
                tmp += ("{0E:%x:%x:%x"%(b,c,d)).upper()
                for item in var:
                    tmp += (":%x"%item).upper()
                tmp += ("}")
            if (b,c)==(0,0):
                tmp = ""
                string += tmp
        elif tmp == 0xf:
            b,c,d = struct.unpack(">3H" , buffer.read(6))
            if d == 0:
                string += ("{0F:%x:%x:%x}"%(b,c,d)).upper()
            else:
                var = struct.unpack(">%dH"%(8/2) , buffer.read(8))
                string += ("{0F:%x:%x:%x"%(b,c,d)).upper()
                for item in var:
                    string += (":%x"%item).upper()
                string += ("}")
        elif tmp >> 8 == 0xe0:
            string += ("{%x}"%(tmp)).upper()
        else:
            string += (data.decode("utf-16be"))
    return string

def unpack_text(fn):
    print(fn)
    fs = open("Japanese/%s"%fn , 'rb')
    dec_size = struct.unpack("I", fs.read(4))[0]
    dec_size2 = struct.unpack("I", fs.read(4))[0]
    lzdata = fs.read()
    lz = lz11()
    decdata = lz.decompress_nlzss(lzdata)
    fp = StringIO(decdata)
    fp.seek(0)
    pos = 0x20
    fp.seek(pos)
    while pos < len(decdata):
        fp.seek(pos)
        sig = fp.read(4)
        if sig == "LBL1":
            block_size, = struct.unpack(">I" , fp.read(4))
            padding = fp.read(8)
            block = fp.read(block_size)
            if block_size%0x10 != 0:
                null = fp.read(0x10 - block_size%0x10)
            pos = fp.tell()
        if sig == "ATR1":
            block_size, = struct.unpack(">I" , fp.read(4))
            padding = fp.read(8)
            block = fp.read(block_size)
            if block_size%0x10 != 0:
                null = fp.read(0x10 - block_size%0x10)
            pos = fp.tell()
        if sig == "TSY1":
            block_size, = struct.unpack(">I" , fp.read(4))
            padding = fp.read(8)
            block = fp.read(block_size)
            if block_size%0x10 != 0:
                null = fp.read(0x10 - block_size%0x10)
            pos = fp.tell()
        if sig == "TXT2":
            block_size, = struct.unpack(">I" , fp.read(4))
            padding = fp.read(8)
            tmp2 = fp.tell()
            block = fp.read(block_size)
            if block_size%0x10 != 0:
                null = fp.read(0x10 - block_size%0x10)
            t_buffer = StringIO()
            t_buffer.write(block)
            blen = len(block)
            t_buffer.seek(0)
            nums, = struct.unpack(">I" , t_buffer.read(4))
            index = t_buffer.read(nums * 4)
            dest = codecs.open("text/%s.txt"%fn,'wb','utf-16')

            for i in xrange(nums):
                offset1, = struct.unpack(">I" , index[i*4:i*4+4])
                t_buffer.seek(offset1)
                print(hex(offset1 + tmp2))
                string = readUString(t_buffer,blen)
                string = string.replace("\r" , "")
                string = string.replace("\n" , "\r\n")
                dest.write("#### %d ####\r\n%s{end}\r\n\r\n"%(i+1,string))
            dest.close()
            pos = fp.tell()
    fp.flush()
    fs.close()
fl = dir_fn("Japanese")
for fn in fl:
    fn = fn.split("\\")[-1]
    unpack_text(fn)







