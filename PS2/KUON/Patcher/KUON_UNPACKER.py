import struct
import os
def unpack_bnd(pack_name):
    inis = open("kuon.ini" ,"wb")
    fp = open(pack_name , 'rb')
    fp.seek(0xc)
    nums = struct.unpack("I" , fp.read(4))[0]
    tmp = fp.tell()
    for i in xrange(nums):
        fp.seek(tmp)
        file_id , offset, size ,noff = struct.unpack("4I" , fp.read(16))
        tmp = fp.tell()
        fp.seek(noff)
        name = fp.read(0x40).split("\x00")[0]
        fp.seek(offset)
        data = fp.read(size)
        folder = "%s_unpacked//%s"%(pack_name , name)
        folder = "//".join(folder.split("//")[:-1])
        print(name)
        print(folder)
        if not os.path.exists(folder):
            os.makedirs(folder)
        dest = open("%s_unpacked//%s"%(pack_name , name) , 'wb')
        dest.write(data)
        dest.close()
        inis.write("%d\t%08x\t%08x\t%s\t\r\n"%(file_id , offset,size,name))
    fp.close()
unpack_bnd("all.bnd")
