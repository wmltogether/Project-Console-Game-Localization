# -*- coding:utf-8 -*-

import codecs,fnmatch,struct,os

fl = os.listdir('cg')
for fn in fl:
    if os.path.isdir('cg/'+fn):
        continue
    dn = os.path.splitext(fn)[0]
    print dn
    fn = 'cg/'+fn
    if not os.path.exists('cg/'+dn):
        os.makedirs('cg/'+dn)
    
    fp = open(fn,'rb')
    num = struct.unpack('I',fp.read(4))[0]
    for i in xrange(num):
        fp.seek(4 + i * 4)
        fileoffset = struct.unpack('I',fp.read(4))[0]
        if i == num - 1:
            size = os.path.getsize(fn) - fileoffset
        else:
            size = struct.unpack('I',fp.read(4))[0] - fileoffset
        fp.seek(fileoffset)
        dat = fp.read(size)
        if dat[:4] == '\x00\x01\x01\x00':
            dest = open('cg/%s/%04d.tga'%(dn,i),'wb')
        elif dat[:4] == '\x00\x00\x02\x00':
            dest = open('cg/%s/%04d.tga'%(dn,i),'wb')
        else:
            dest = open('cg/%s/%04d.bin'%(dn,i),'wb')
        dest.write(dat)
        dest.close()
    fp.close()

