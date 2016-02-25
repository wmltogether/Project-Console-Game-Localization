# -*- coding:utf-8 -*-
import codecs,fnmatch,struct,os

def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
    
def pack0(filedir):
    print filedir
    aa = filedir+'.pak'
    bb = aa.split("\\")[-1].replace("__" , "\\")
    fp = open(bb[:-4] + ".bin",'wb')
    fl = dir_fn(filedir)
    fl = [fn for fn in fl]
    num = len(fl)
    fp.write(struct.pack('I',num))
    fp.seek(num*4+4)

    ol = []
    for fn in fl:
        if fp.tell()%0x10 != 0:
            fp.seek((fp.tell()/0x10+1)*0x10)
        ol.append(fp.tell())
        dat = open(fn,'rb').read()
        fp.write(dat)

    if fp.tell()%0x400 != 0:
        fp.seek((fp.tell()/0x400+1)*0x400-1)
        fp.write('\x00')

    fp.seek(4)
    for o in ol:
        fp.write(struct.pack('I',o))
    fp.close()

def pack(filedir):
    print filedir
    fp = open(filedir.replace("pak_files" , "import")+'.pak','wb')
    fl = dir_fn(filedir)
    fl = [fn for fn in fl]
    num = len(fl)
    fp.write(struct.pack('I',num))
    fp.seek(num*4+4)

    ol = []
    for fn in fl:
        if fp.tell()%0x10 != 0:
            fp.seek((fp.tell()/0x10+1)*0x10)
        ol.append(fp.tell())
        dat = open(fn,'rb').read()
        fp.write(dat)

    if fp.tell()%0x400 != 0:
        fp.seek((fp.tell()/0x400+1)*0x400-1)
        fp.write('\x00')

    fp.seek(4)
    for o in ol:
        fp.write(struct.pack('I',o))
    fp.close()


fl = os.listdir('pak_bin')
for fn in fl:
    if not os.path.isdir('pak_bin\\'+fn):
        continue
    dn = os.path.splitext(fn)[0]
    filedir = 'pak_bin\\'+dn
    pack0(filedir)


fl = os.listdir('pak_files\\cg')
for fn in fl:
    if not os.path.isdir('pak_files\\cg\\'+fn):
        continue
    dn = os.path.splitext(fn)[0]
    filedir = 'pak_files\\cg\\'+dn
    pack(filedir)

fl = os.listdir('pak_files\\bin')
for fn in fl:
    if not os.path.isdir('pak_files\\bin\\'+fn):
        continue
    dn = os.path.splitext(fn)[0]
    filedir = 'pak_files\\bin\\'+dn
    pack(filedir)
    
fl = os.listdir('pak_files\\flash')
for fn in fl:
    if not os.path.isdir('pak_files\\flash\\'+fn):
        continue
    dn = os.path.splitext(fn)[0]
    filedir = 'pak_files\\flash\\'+dn
    pack(filedir)