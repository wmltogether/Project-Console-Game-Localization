# -*- coding: utf-8 -*-
import codecs
import struct
import os
from cStringIO import StringIO
def GetTable():
        fp = codecs.open("dst.TBL",'rb','utf-16')
        lines = fp.readlines()
        base_tbl = {}
        for line in lines:
            if "=" in line:
                code,char = line.split("=")[:2]
                char = char.replace("\r" , "")
                char = char.replace("\n" , "")
                base_tbl[char] = int(code,16)
        return base_tbl

def makestr(lines):
    string_list = []
    head_list = []
    num = len(lines)
    for index,line in enumerate(lines):
        if u'####' in line:
            head_list.append(line[5:-7])
            i = 1
            string = ''
            while True:
                if index+i >= num:
                    break
                if '####' in lines[index+i]:
                    break
                string += lines[index+i]
                i += 1
            string_list.append(string[:-4])
    return string_list

def findctr_code(string , original_text):
    if not "}" in string:
        print(u"error :[%s] >> } code is missing \n text: [%s]"%(string , original_text))
        return ""
    pos = 0
    ctr_str = ""
    mark = 0
    while pos < len(string):
        char = string[pos]
        if char == "{":
            ctr_str += char
            mark = 1
            pos += 1

        elif char == "}":
            ctr_str += char
            break
        else:
            ctr_str += char
            mark = 1
            pos += 1
    return ctr_str[1:-1]

def string2hex(string , base_tbl):
    string = string.replace("\r" , "")
    string = string.replace("\n" , "\n")
    hex = ""
    pos = 0
    tmp_ctr = ""
    while pos < len(string):
        char = string[pos]
        if char == "{":
            ctr_str = findctr_code(string[pos:],string)
            items = ctr_str
            tmp_ctr += struct.pack("H" , int(items,16))
            pos += len(ctr_str) + 2
        else:
            if char == ' ':
                tmp_ctr += struct.pack("H" , 0xfd02)
            elif char == '\n':
                tmp_ctr += struct.pack("H" , 0xfd01)  
            elif char in base_tbl:
                tmp_ctr += struct.pack("H" , base_tbl[char])
            else:
                print(u"error :%s is not in tbl"%char)
            pos += 1
    return tmp_ctr


def export_msg(fn):
    base_tbl = GetTable()
    base = open(fn , "rb")
    fp = StringIO()
    fp.write(base.read())
    fp.seek(0)
    cnlines = codecs.open("t3b_cn.txt" , "rb" , "utf-16").readlines()
    index_end_offset  = struct.unpack("I" , fp.read(4))[0]
    string_list = makestr(cnlines)
    nums = len(string_list)
    fp.seek(0x18c48)
    fp.truncate()
    tmp = fp.tell()
    for i in xrange(nums):
        fp.seek(0,2)
        tmp = fp.tell()
        string = string2hex(string_list[i] , base_tbl)
        fp.write(string)
        fp.seek(0x5dfc + i*0xc)
        fp.write(struct.pack("I" , tmp))
        fp.write(struct.pack("I" , len(string)/2))
        fp.seek(0,2)
    data = fp.getvalue()
    dest = open("import\\00000019.lang" , "wb")
    dest.write(data)
    dest.close()

os.system("FontCreator.exe")
export_msg("00000019.lang")


