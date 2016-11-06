import os
import sys
import time
import struct
from nlzss import *

def decompress_files(name):
    print("loading:%s"%name)
    lz = lz11()
    fp = open(name, "rb")
    dec_size = struct.unpack("I", fp.read(4))[0]
    dec_size2 = struct.unpack("I", fp.read(4))[0]
    data = fp.read()
    dec = lz.decompress_nlzss(data)
    dest = open(os.path.basename(name)+".dec","wb")
    dest.write(dec)
    dest.close()
    fp.close()

def compress_file(name):
    print("loading:%s"%name)
    lz = lz11()
    fp = open(name, "rb")
    data = fp.read()
    dest2 = open(os.path.basename(name)+".lz","wb")
    dest2.write(struct.pack("I",len(data)))
    dest2.write(struct.pack("I",len(data)))
    print("compressing...")
    dest2.write(lz.compress_nlzss(data,13))
    dest2.close()
    fp.close()
    
def main(flag):
    t0 = time.time()
    t1 = time.time()
    if len(flag)<=1:
        flag.append('')
    if len(flag)>1 and flag[1] == '-c':
        compress_file(flag[2])
    elif len(flag)>1 and flag[1] == '-d':
        decompress_files(flag[2])
    else:
        print('--usage: \n lz_compresstool <command> <name>\n       -c compress files\n       -d decompress files')
        print(("error flag:%s"%flag))
    print(t1-t0)
    
if __name__ == '__main__':
    import sys
    flag = sys.argv
    main(flag)
    os.system('pause')