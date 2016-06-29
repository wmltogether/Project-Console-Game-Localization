import codecs,struct,os

def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst

class NISDAT(object):
    def __init__(self):
        self.nums = 0

    def pack_start(self , folder, output_name="import\\start.dat"):
        fl = dir_fn((folder))
        self.nums = len(fl)
        dest = open(output_name , "wb")
        dest.write(struct.pack("I" , self.nums))
        dest.write("\x00" * 0x18 * self.nums)
        dest.write("\x00" * (0x10 - dest.tell()%0x10))
        dest.seek(0,2)
        pos = dest.tell()
        if not pos%0x10 == 0:
            dest.write("\x00" * (0x10 - pos%0x10))
        pos = dest.tell()
        for i in xrange(self.nums):
            fn = fl[i]
            base_name = os.path.basename(fn).upper()
            fs = open(fn , "rb")
            data = fs.read()
            dest.seek(4 + i * 0x18)
            dest.write(base_name)
            dest.seek(4 + i * 0x18 + 0x10)
            dest.write(struct.pack("I" , pos))
            dest.write(struct.pack("I" , len(data)))
            dest.seek(pos)
            dest.write(data)
            dest.seek(0,2)
            pos = dest.tell()
            if not pos%0x10 == 0:
                dest.write("\x00" * (0x10 - pos%0x10))
                pos = dest.tell()
            fs.close()
        dest.close()
            
        
        
    def unpack_start(self, fn):
        fp = open(fn , "rb")
        self.nums = struct.unpack("I" , fp.read(4))[0]
        for i in xrange(self.nums):
            fp.seek(0x4 + 0x18 * i)
            _current_name = fp.read(0x10).split("\x00")[0]
            _current_offset = struct.unpack("I" , fp.read(4))[0]
            _current_size = struct.unpack("I" , fp.read(4))[0]
            print(_current_name)
            if not os.path.exists("%s_unpacked"%(fn)):os.makedirs("%s_unpacked"%(fn))
            dest = open("%s_unpacked//%s"%(fn , _current_name) , "wb")
            fp.seek(_current_offset)
            data = fp.read(_current_size)
            dest.write(data)
            dest.close()
        fp.close()

nisd = NISDAT()
nisd.pack_start("start.dat_unpacked" , output_name="import\\start.dat")

