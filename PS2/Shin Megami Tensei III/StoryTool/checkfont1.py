# -*- coding:utf-8 -*-
import codecs
import os
from JsonHelper import JsonHelper
class ELFCHUNK:
    def __init__(self):
        self.TEXTLIST = []
class LocText(object):
    def __init__(self):
        self.ELFTAG = ""
        self.TEXT_0_JP = ""
        self.TEXT_1_CN = ""
def GetTable(tbl_name):
    xx = 0
    fp = codecs.open(tbl_name, 'rb', 'utf-16')
    lines = fp.readlines()
    base_tbl = {}
    for line in lines:
        if "=" in line:
            code, char = line.split("=")[:2]
            char = char.replace("\r", "")
            char = char.replace("\n", "")
            if (xx < 2373):
                base_tbl[char] = int(code, 16)
            xx += 1
    return base_tbl

def docheck():
    sss = ""
    bbb = []
    ttt = GetTable("charlist_making/ch.tbl")
    elftable = ELFCHUNK()
    elftable.__dict__ = JsonHelper.Serialize(codecs.open("ELF_HACKS.json", "rb", "utf-8").read())
    vLocText = LocText()
    for i in xrange(len(elftable.TEXTLIST)):
        vLocText.__dict__ = elftable.TEXTLIST[i]
        cntxt = vLocText.TEXT_1_CN
        for chrr in cntxt:
            if (chrr in ttt):
                pass
            else:
                if (chrr in bbb):
                    pass
                else:
                    bbb.append(chrr)
    return "".join(bbb)

def main():
    print(docheck())
    pass
main()