# -*- coding: utf-8 -*-
import os
import struct
import codecs
import operator
def generate_sjis():
    s_list = []
    n = 0
    for j0 in xrange(0x81,0x99):
        for j1 in xrange(0x40,0xfd):
            if ((j0  * 0x100) + j1) >= 0x889F and ((j0  * 0x100) + j1) <= 0x9872:
                if (j1 != 0x7f):
                    n+=1
                    s_list.append( (j0  * 0x100) + j1)
    print(n)
    return s_list
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
r_tbl = []
fl = os.listdir("cn-text")
for fn in fl:
    fp = codecs.open("cn-text//%s"%fn , "rb" , "utf-16")
    data = fp.read()
    data = data.replace("\r" , "")
    data = data.replace("\n" , "")
    for char in data:
        if char in tbl:
            pass
        elif char in base_tbl:
            pass
        else:
            tbl.append(char)
for items in tbl:
    count_value = tbl.count(items)
    n_dict[items] = count_value
sorted_n_dict = sorted(n_dict.iteritems(), key=lambda x : x[1], reverse=True)

for (item , counts) in sorted_n_dict:
    if item in r_tbl:
        pass
    else:
        r_tbl.append(item)
print(u"统计出现字数：%d"%len(r_tbl))
dest = codecs.open(u"字符统计.txt" , 'w' , 'utf-16')
dest.write("".join(r_tbl))
dest.close()
s_list = generate_sjis()
dest = codecs.open(u"ch.tbl" , 'wb' , 'utf-16')
if len(r_tbl) > len(s_list):
    print(u"error: 错误，字符太多了，超出了2965个汉字的上限")
    
else:
    for i in xrange(len(r_tbl)):
        char = r_tbl[i]
        code = s_list[i]
        dest.write("%04x=%s\r\n"%(code,char))
dest.close()



 
