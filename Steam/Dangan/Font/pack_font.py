# -*- coding:utf-8 -*-

import codecs,fnmatch,struct,os
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            ext = name.split('.')[-1]
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst

def pack(filedir):
    print filedir
    fp = open('font\\font.pak','wb')
    fl = dir_fn(filedir)
    num = len(fl)
    fp.write(struct.pack('I',num))
    fp.seek(num*4+4)

    ol = []
    for fn in fl:
        print(fn)
        if fp.tell()%0x40 != 0:
            fp.seek((fp.tell()/0x40+1)*0x40)
        ol.append(fp.tell())
        dat = open(fn,'rb').read()
        fp.write(dat)
    if fp.tell()%0x40 != 0:
        fp.seek((fp.tell()/0x40+1)*0x40)
    ol.append(fp.tell())

    fp.seek(4)
    for o in ol:
        fp.write(struct.pack('I',o))
    fp.close()

pack('font\\font')

