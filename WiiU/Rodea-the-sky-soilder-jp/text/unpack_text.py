import codecs,struct,os
from glob import iglob
from cStringIO import StringIO
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def readUString(buffer):
    data = ""
    string = u""
    while True:
        fbyte= buffer.read(1)
        sbyte = buffer.read(1)
        if (ord(fbyte),ord(sbyte)) == (0,0):
            break
        data = (fbyte + sbyte)
        tmp, = struct.unpack(">H" , data)
        if tmp == 0xe:
            b,c,d,e = struct.unpack(">4H",buffer.read(8))
            string += ("{0E:%x:%x:%x:%x}"%(b,c,d,e)).upper()
        else:
            string += (data.decode("utf-16be"))
    return string

def unpack_text(fn):
    fp = open("%s"%fn , 'rb')
    dest = codecs.open("JPtext/%s.txt"%fn.replace("\\", "__") , "wb" , 'utf-16')
    pos = 0x0
    fp.seek(pos)
    sig = fp.read(4)
    if sig == "TXTD":
            fp.seek(0x8)
            nums, = struct.unpack(">I" , fp.read(4))
            fp.seek(0x20)
            tmp = fp.tell()
            for i in xrange(nums):
                fp.seek(tmp)
                offset1, = struct.unpack(">I" , fp.read(4))
                tmp = fp.tell()
                fp.seek(offset1)
                string = readUString(fp)
                string = string.replace("\n" , "\r\n")
                dest.write("#### %d ####\r\n%s{end}\r\n\r\n"%(i+1,string))
            dest.close()
            pos = fp.tell()
    if sig == "TALD":
            fp.seek(0x8)
            nums, = struct.unpack(">I" , fp.read(4))
            fp.seek(0xC)
            nums2, = struct.unpack(">I" , fp.read(4))
            fp.seek(0x20 + nums * 0x10)
            tmp = fp.tell()
            for i in xrange(nums2):
                fp.seek(tmp + 0x14)
                offset1, = struct.unpack(">I" , fp.read(4))
                tmp = tmp + 0x20
                fp.seek(offset1)
                string = readUString(fp)
                string = string.replace("\n" , "\r\n")
                dest.write("#### %d ####\r\n%s{end}\r\n\r\n"%(i+1,string))
            dest.close()
            pos = fp.tell()
    fp.close()
fl = dir_fn("content")
for fn in fl:
    unpack_text(fn)




