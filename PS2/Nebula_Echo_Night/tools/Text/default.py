 # -*- coding: utf-8 -*-
import os
import struct
import codecs
import operator
#
#    JIS X 0208字集的所有字符

#    “第一位字节\\”使用0×81-0×9F、0xE0-0xEF (共47个)
#    “第二位字节\\”使用0×40-0×7E、0×80-0xFC (共188个)
#     base_char.txt里的内容需要固定编码，其他汉字浮动编码
def find_base_jiscode(uchar):
    bin = uchar.encode("cp932")
    code = struct.unpack(">H" , bin)[0]
    return code
def makeccm_info(cndict):
    ccm_file = open(u"ccminfo.ini" , "wb")
    ccm_file.write("[char_nums:%d]\r\n"%(len(cndict) + 0x5f))
    ccm_file.write("%04x,%04x,\r\n"%(0x20 , 0x7e))
    cndict = sorted(cndict.iteritems(), key=lambda x : x[0])
    tmp = []
    for key in cndict:
        print(hex(key[0]))
        if (len(tmp) >= 1) and (tmp[-1] + 1 != key[0]):
            print("%04x,%04x,\r\n"%(tmp[0] , tmp[-1]))
            ccm_file.write("%04x,%04x,\r\n"%(tmp[0] , tmp[-1]))
            tmp = []
        code = key[0]
        tmp.append(code)
    if (len(tmp) >= 1) and (tmp[-1] + 1 != key[0]):
        print("%04x,%04x,\r\n"%(tmp[0] , tmp[-1]))
        ccm_file.write("%04x,%04x,\r\n"%(tmp[0] , tmp[-1]))
    ccm_file.close()

def makeCNTable(nums,base_char_file_name,tbl):
    dest = codecs.open("charlist.txt" ,"wb" ,"utf-16")
    dest.write(" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~")
    fp = codecs.open(base_char_file_name , "rb" , "utf-16")
    base_chars = fp.read()
    base_dict = {}
    for item in base_chars:
        base_dict[find_base_jiscode(item)] = item
    fp.close()
    test_file = codecs.open("cn.tbl" , "wb" , "utf-16")
    new_nums = nums + len(base_chars)
    pos = 0
    v0 = 0x89
    v1 = 0x40
    cndict0 = {}
    cndict = {}
    n = 0
    cndict = cndict0.copy()
    cndict.update(base_dict)
    while pos < nums:
        if (v0 * 0x100 + v1) in base_dict:
            cndict[v0 * 0x100 + v1] = base_dict[v0 * 0x100 + v1]
        else:
            cndict[v0 * 0x100 + v1] = tbl[n]
            n += 1
        if (0x40 <= v1 <= 0x7e) or (0x80 <= v1 <= 0xfc):
            v1  = v1 + 1
        if v1 == 0x7f:
            v1 = 0x80
        if v1 == 0xfd:
            v0 += 1
            v1 = 0x40
        if v0 == 0xa0:
            v0 = 0xe0

        pos += 1
    makeccm_info(cndict)
    cndict = sorted(cndict.iteritems(), key=lambda x : x[0])
    for key in cndict:
        code = key[0]
        char = key[1]
        test_file.write("%04x=%s\r\n"%(code,char))
        dest.write("%s"%char)
    dest.close()




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

def getbasetbl():
    fp = codecs.open("base.TBL",'rb','utf-16')
    lines = fp.readlines()
    base_tbl = []
    for line in lines:
        if "=" in line:
            code,char = line.split("=")[:2]
            char = char.replace("\r\n" , "")
            base_tbl.append(char)
    return base_tbl
base_tbl = getbasetbl()
tbl = []
n_dict = {}
r_tbl = {}
fl = os.listdir("cn-text")
base_chars = codecs.open("base_char.txt" ,"rb" , "utf-16").read()
for fn in fl:
    fp = codecs.open("cn-text//%s"%fn , "rb" , 'utf-16')
    lines = fp.readlines()
    string_list = makestr(lines)
    fp.close()
    for string in string_list:
        string = string.replace("\r\n" , "")
        for char in string:
            if not char in base_tbl:
                if not char in tbl:
                    if not char in base_chars:
                        uchar = char.encode("utf-16")[2:]
                        uchar,= struct.unpack("H" , uchar)
                        r_tbl[char] = uchar
r_tbl = sorted(r_tbl.iteritems(), key=lambda x : x[1])
for key in r_tbl:
    tbl.append(key[0])

nums = len(tbl)
print(len(tbl))


makeCNTable(nums,"base_char.txt",tbl)



