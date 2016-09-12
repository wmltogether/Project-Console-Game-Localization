import os
import struct
import codecs


class ARC(object):
    def __init__(self, name):
        self.name = name
        self.sig = "MPK\x00"
        pass

    def patch_arc(self, input_name, patch_folder):
        fp = open(input_name, "rb+")
        sig = fp.read(4)
        if (sig != self.sig):
            fp.close()
            return None
        fp.seek(8)
        nums = struct.unpack("I", fp.read(4))[0]
        
        for i in xrange(nums):
            fp.seek(0x40 + 0x100 * i)
            
            tmp_ofs = fp.tell()
            null = struct.unpack("I", fp.read(4))[0]
            id = struct.unpack("I", fp.read(4))[0]
            tmp_ofs = fp.tell()
            offset = struct.unpack("Q", fp.read(8))[0]
            size = struct.unpack("Q", fp.read(8))[0]
            size = struct.unpack("Q", fp.read(8))[0]
            name = fp.read(0x30).split("\x00")[0]
            if (os.path.exists("%s//%s" % (patch_folder, name))):
                # need patch
                print("got %s//%s ", patch_folder, name)
                pt = open("%s//%s" % (patch_folder, name), "rb")
                data = pt.read()
                fsize = len(data)
                if (fsize < size):
                    # inject
                    fp.seek(offset)
                    fp.write(data)
                    fp.write("\x00" * (size - fsize))
                    fp.seek(tmp_ofs + 8)
                    fp.write(struct.pack("Q", size))
                    fp.write(struct.pack("Q", size))
                    print("inject:%08x,%d" % (offset, size))
                    pass
                else:
                    # extend

                    fp.seek(0, 2)

                    o = fp.tell()
                    if (o % 0x800 != 0):
                        fp.write("\x00" * (0x800 - o % 0x800))
                    o2 = fp.tell()
                    fp.write(data)
                    o = fp.tell()
                    if (o % 0x800 != 0):
                        fp.write("\x00" * (0x800 - o % 0x800))
                    fp.seek(tmp_ofs)
                    fp.write(struct.pack("Q", o2))
                    fp.write(struct.pack("Q", size))
                    fp.write(struct.pack("Q", size))
                    print("extend:%08x,%d" % (o2, size))

                    pass
                pt.close()
        fp.close()
        pass

    def unpack_arc(self, dst_folder):
        fp = open(self.name, "rb")
        sig = fp.read(4)
        if (sig != self.sig):
            fp.close()
            return None
        fp.seek(8)
        nums = struct.unpack("I", fp.read(4))[0]
        fp.seek(0x10)
        for i in xrange(nums):
            fp.seek(0x40 + 0x100 * i)
            tmp_ofs = fp.tell()
            null = struct.unpack("I", fp.read(4))[0]
            id = struct.unpack("I", fp.read(4))[0]
            offset = struct.unpack("Q", fp.read(8))[0]
            size = struct.unpack("Q", fp.read(8))[0]
            size = struct.unpack("Q", fp.read(8))[0]
            name = fp.read(0x30).split("\x00")[0]
            fp.seek(offset)
            data = fp.read(size)
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)
            dest = open("%s//%s" % (dst_folder, name), "wb")
            dest.write(data)
            dest.close()
        fp.close()
