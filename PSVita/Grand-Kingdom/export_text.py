# -*- coding:utf-8 -*-  
import os
import codecs
import struct
from glob import iglob

def uni2int(char):
    c = char.encode("utf-16")[2:]
    return struct.unpack("H",c)[0]

def export_text(fname):
    fp = open(fname, "rb")
    fp.seek(0x20)
    basename = os.path.basename(fname) + ".txt"
    nums = struct.unpack("I", fp.read(4))[0]
    n_size = struct.unpack("I", fp.read(4))[0]
    dest = codecs.open("jp-text//%s"%basename, "wb", "utf-16")
    pfile = open("p//%s"%basename, "wb")
    pfile.write("#%08x\r\n"%(os.path.getsize(fname) - n_size))
    print("#%08x\r\n"%(os.path.getsize(fname) - n_size))
    for i in xrange(nums):
        _id,_length = struct.unpack("2I", fp.read(8))
        text = fp.read(_length)[:-1]
        string = text.decode("utf-8")
        string = string.replace("\n", "\r\n")
        c = ""
        for item in string:
            if 0x9fa5 <= uni2int(item) <= 0xff00:
                c += "{CODE:%04x}"%uni2int(item)
            else:
                c += item
        dest.write("#### %d ####\r\n%s\r\n\r\n"%(i, c))
        pfile.write("%d,%d,\r\n"%(i, _id))
    dest.close()
    fp.close()
    pfile.close()
    pass

fl = iglob("MESFONT/*.mes")
for fn in fl:
    print(fn)
    export_text(fn)
