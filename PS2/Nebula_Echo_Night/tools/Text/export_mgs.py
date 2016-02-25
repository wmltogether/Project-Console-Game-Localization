 # -*- coding: utf-8 -*-
import os
import struct
import codecs
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def readstrings(binaryReader):
    string = ""
    while True:
        char = binaryReader.read(1)
        if ord(char) == 0:
            break
        else:
            string += char
    return string
def unpack_msg(name):
    fp = open("jpdata//%s"%name ,"rb")
    fp.seek(0x4)
    fmg_size, = struct.unpack("I" , fp.read(4))
    fp.seek(0x10)
    nums, = struct.unpack("I" , fp.read(4))
    boffset, = struct.unpack("I" , fp.read(4))
    fp.seek(boffset)
    dest = codecs.open("jp-text//%s.txt"%name , "wb" , "utf-16")
    n = 1
    for i in xrange(nums):
        fp.seek(boffset + 0x4 * i)
        offset, = struct.unpack("I" , fp.read(4))
        if not offset == 0:
            fp.seek(offset)
            string = readstrings(fp)
            string = string.decode("cp932")
            
            string = string.replace(r"#*" ,"{232A}")
            string = string.replace("\n" ,"\r\n")
            dest.write("#### %d,%d ####\r\n%s{end}\r\n\r\n"%(n , i , string))
            n += 1
    dest.close()
    fp.close()
def main():
    fl = os.listdir("jpdata")
    print(fl)
    for fn in fl:
        if ".fmg" in fn[-4:].lower():
            unpack_msg(fn)

if __name__ == '__main__':
    main()

