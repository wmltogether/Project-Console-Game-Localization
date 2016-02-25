# -*- coding:utf-8 -*-
import codecs,fnmatch,struct,os,shutil
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def check_pak(fname):
    fp = open(fname , "rb")
    nums = struct.unpack("I" , fp.read(4))[0]
    first_offset = struct.unpack("I" , fp.read(4))[0]
    bb = 0
    if (nums * 4 + 4)%0x10 != 0:
        bb = 0x10 - (nums * 4 + 4)%0x10 + (nums * 4 + 4)
    if bb > 0 and bb == first_offset:
        return True
    else:
        return False

fl = dir_fn("pak_files\\bin")
for fn in fl:
    if fn[-4:].lower() == ".bin":
        print(fn)
        if check_pak(fn) == True:
            fn_new  = fn.replace("\\" , "__")[:-4] + ".pak"
            shutil.copy(fn , "pak_bin\\%s"%fn_new)


