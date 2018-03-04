# -*- coding:utf-8 -*-
import codecs
import os
from JsonHelper import JsonHelper
from pypinyin import lazy_pinyin

def GetTable(tbl_name):
    fp = codecs.open(tbl_name, 'rb', 'utf-16')
    lines = fp.readlines()
    base_tbl = {}
    for line in lines:
        if "=" in line:
            code, char = line.split("=")[:2]
            char = char.replace("\r", "")
            char = char.replace("\n", "")
            base_tbl[char] = int(code, 16)
    return base_tbl
ascii_chars = u" !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
base_tbl = GetTable("base.TBL")

class ELFCHUNK:
    def __init__(self):
        self.TEXTLIST = []
class LocText(object):
    def __init__(self):
        self.ELFTAG = ""
        self.TEXT_0_JP = ""
        self.TEXT_1_CN = ""

name_table = u"高尾祐子新田勇橘千晶冰川圣丈二"

kanjinormal = codecs.open("kanji_normal3500.txt", "rb", "utf-16").read()
kanjinormal = name_table + kanjinormal
keyboarddata = codecs.open("name_ent_gb2132.txt", "rb", "cp936").read()
kanjinormal = kanjinormal + keyboarddata
fl = os.listdir("cn-text")
dst = codecs.open("charlist_making/charlist.txt", "wb", "utf-16")
zlist = []
for char in kanjinormal:
    if (char in base_tbl):
        pass
    elif char == "\r":
        pass
    elif char == "\n":
        pass
    elif char in ascii_chars:
        pass
    elif char in zlist:
        pass
    else:
        zlist.append(char)

elftable = ELFCHUNK()
elftable.__dict__ = JsonHelper.Serialize(codecs.open("ELF_HACKS.json", "rb", "utf-8").read())
vLocText = LocText()
for i in xrange(len(elftable.TEXTLIST)):
    vLocText.__dict__ = elftable.TEXTLIST[i]
    text = vLocText.TEXT_1_CN
    for char in text:
        if (char in base_tbl):
            pass
        elif char == "\r":
            pass
        elif char == "\n":
            pass
        elif char in ascii_chars:
            pass
        elif char in zlist:
            pass
        else:
            zlist.append(char)
            
elftable = ELFCHUNK()
elftable.__dict__ = JsonHelper.Serialize(codecs.open("FIELD_TABLE.json", "rb", "utf-8").read())
vLocText = LocText()
for i in xrange(len(elftable.TEXTLIST)):
    vLocText.__dict__ = elftable.TEXTLIST[i]
    text = vLocText.TEXT_1_CN
    for char in text:
        if (char in base_tbl):
            pass
        elif char == "\r":
            pass
        elif char == "\n":
            pass
        elif char in ascii_chars:
            pass
        elif char in zlist:
            pass
        else:
            zlist.append(char)

for fn in fl:
    if os.path.exists("cn-text/%s" % fn):
        print(fn)
        cn_lines = codecs.open("cn-text/%s" %
                               fn, "rb", "utf-16").read()
        for char in (cn_lines):
            if (char in base_tbl):
                pass
            elif char == "\r":
                pass
            elif char == "\n":
                pass
            elif char in ascii_chars:
                pass
            elif char in zlist:
                pass
            else:
                zlist.append(char)
dst.write("".join(zlist))
dst.close()
if (os.path.exists("charlist_making\\font0_ch.fnt")):
    os.remove("charlist_making\\font0_ch.fnt")
if (os.path.exists("charlist_making\\ch.tbl")):
    os.remove("charlist_making\\ch.tbl")
if (os.path.exists("charlist_making\\ch.tbl")):
    fs = open("charlist_making\\ch.tbl", "rb")
    data = fs.read()
    dst = open("ch.tbl", "wb")
    dst.write(data)
    fs.close()
    dst.close()
os.chdir(".\\charlist_making")
print(u"generating fonts")
os.popen("AltusFontTool.exe")
