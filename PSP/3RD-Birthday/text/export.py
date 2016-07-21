# -*- coding: utf-8 -*-
import codecs
import struct
import os
def GetTable():
        fp = codecs.open("jp.TBL",'rb','utf-16')
        lines = fp.readlines()
        base_tbl = {}
        for line in lines:
            if "=" in line:
                code,char = line.split("=")[:2]
                char = char.replace("\r" , "")
                char = char.replace("\n" , "")
                base_tbl[int(code,16)] = char
        return base_tbl

def binary2String(data , base_tbl):
    string = u""
    for i in xrange(0,len(data),2):
        tmp = struct.unpack("H", data[i:i+2])[0]
        if tmp == 0:
            string += "{0000}"
        elif 0 < tmp < 0x76d:
            if tmp in base_tbl:
                string += u"%s"%(base_tbl[tmp])
            else:
                string += "{%04x}"%tmp
        elif tmp == 0xFD01:
            string += "\r\n"
        elif tmp == 0xfd02:
            string += " "
        else:
            string += "{%04x}"%tmp
    return string

def export_msg(fn):
    base_tbl = GetTable()
    fp = open(fn , "rb")
    dest = codecs.open("t3b_jp.txt" , "wb" , "utf-16")
    index_end_offset  = struct.unpack("I" , fp.read(4))[0]
    nums = (0x18c48 - index_end_offset)/12
    fp.seek(index_end_offset)
    for i in xrange(nums):
        fp.seek(0x5dfc + i*0xc)
        offset,size,null = struct.unpack("3I" , fp.read(12))
        size = size * 2
        fp.seek(offset)
        data = fp.read(size)
        string = binary2String(data , base_tbl)
        dest.write("#### %d ####\r\n%s\r\n\r\n"%(i , string))
    dest.close()
    fp.close()

export_msg("00000019.lang")


