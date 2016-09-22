import codecs
import os
import struct
from cStringIO import StringIO


def export_stringlistdatabase(data):
    br = StringIO(data)
    br.seek(0)
    dst_lst = []
    id_list = []
    nums = struct.unpack("I", br.read(4))[0]
    for i in xrange(nums):
        br.seek(0x4 + 0xc * i)
        _id = struct.unpack("I", br.read(4))[0]
        _char_num = struct.unpack("I", br.read(4))[0]
        _offset = struct.unpack("I", br.read(4))[0]
        _offset += 4
        br.seek(_offset)
        print(hex(_offset))
        string = br.read(_char_num * 3 + 2).split("\x00\x00")[0]
        string = string.decode("utf-8")
        string = string.replace("\r", "")
        string = string.replace("\n", "\r\n")
        dst_lst.append(string)
        id_list.append(_id)
    return dst_lst


def export_keyitemdatabase(data):
    br = StringIO(data)
    br.seek(0)
    dst_lst = []
    nums = struct.unpack("I", br.read(4))[0]
    for i in xrange(nums):
        br.seek(0x4 + 0x10 * i)
        _id = struct.unpack("I", br.read(4))[0]
        _char_num = struct.unpack("I", br.read(4))[0]
        _offset = struct.unpack("I", br.read(4))[0]
        _id1 = struct.unpack("I", br.read(4))[0]
        _offset += 4
        br.seek(_offset)
        print(hex(_offset))
        string = br.read(_char_num * 3 + 2).split("\x00\x00")[0]
        string = string.decode("utf-8")
        string = string.replace("\r", "")
        string = string.replace("\n", "\r\n")
        dst_lst.append(string)
    return dst_lst


def export_text(name):
    print(name)
    fp = open("data//%s" % name, "rb")
    data = fp.read()
    if ("collectionitemdatabase" in name):
        lst = export_keyitemdatabase(data)
    elif ("keyitemdatabase" in name):
        lst = export_keyitemdatabase(data)
    else:
        lst = export_stringlistdatabase(data)
    dst = codecs.open("jp-text//%s.txt" % name, "wb", "utf-16")
    for i in xrange(len(lst)):
        string = lst[i]
        dst.write(u"#### %d ####\r\n%s\r\n\r\n" % (i + 1, string))
    dst.close()
    fp.close()


export_text("collectionitemdatabase.dat")
export_text("keyitemdatabase.dat")
export_text("stringlistdatabase.dat")
