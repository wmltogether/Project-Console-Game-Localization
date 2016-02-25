# -*- coding: utf-8 -*-
import os,codecs,struct
import zlib
import math
from cStringIO import StringIO


def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst

def patch_eboot(dest_path , patch_path):
	fp = open(patch_path , "rb")
	data = fp.read()
	dest = open(dest_path , "wb")
	dest.write(data)
	dest.close()
	fp.close()
