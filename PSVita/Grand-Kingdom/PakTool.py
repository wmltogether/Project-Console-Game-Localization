import codecs
import os
import struct
import sys
import zlib


class Content(object):
    def __init__(self):
            self.index_pos = 0
            self.decompress_size = 0
            self.compress_size = 0
            self.offset = 0
            self.filename = ""
            self.compressed = False
            pass

class PAK(object):

    def __init__(self):
        self.content = []
        pass

    def Unpack(self , fname , dstPath):
        self.content = []
        fp  = open(fname , "rb")

        fp.seek(0x100)
        content_path = []
        dir_nums,file_nums,data_offset = struct.unpack("3I", fp.read(12))

        for i in xrange(dir_nums):
            fp.seek(0x100 + 0xc + (0x100 + 0x4) * i)
            _name = fp.read(0x100).split("\x00")[0]
            _adr = struct.unpack("I", fp.read(4))[0]
            self.getContent(fp , _adr, _name)

            pass

        v = Content()
        for v in self.content:
            path = dstPath + "\\" + v.filename
            if not os.path.exists( os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            print(path)
            print("Index pos :%08x"%v.index_pos)
            print("Offset :%08x"%v.offset)
            print("Size :%08x"%v.compress_size)
            print("Compressed :%d"%v.compressed)
            with open(path ,"wb")as dst:
                fp.seek(v.offset)
                decdata = ""
                if v.compressed == True:

                    outLength,inLength = struct.unpack("2I", fp.read(8))
                    zdata = fp.read(inLength)
                    decdata = zlib.decompress(zdata)
                else:
                    decdata = fp.read(v.compress_size)
                dst.write(decdata)


    def getContent(self, fp ,_adr, _name):
        fp.seek(_adr)
        dir_nums, file_nums = struct.unpack("2I", fp.read(8))
        base = fp.tell()
        basename = _name
        for i in xrange(dir_nums):
            fp.seek(base + 0x104*i)
            _name = fp.read(0x100).split("\x00")[0]
            _adr = struct.unpack("I", fp.read(4))[0]

            self.getContent(fp , _adr, (basename + '\\' + _name))
        fp.seek(base + 0x104 * dir_nums)
        for j in xrange(file_nums):
            _name = fp.read(0x100).split("\x00")[0]
            m = fp.tell()
            _decompress_size = struct.unpack("I", fp.read(4))[0]
            _compress_size = struct.unpack("I", fp.read(4))[0]

            _adr = struct.unpack("I", fp.read(4))[0]

            m_content = Content()
            m_content.index_pos = m
            m_content.filename = (basename + "\\" + _name)
            m_content.decompress_size = _decompress_size
            m_content.compress_size = _compress_size
            m_content.offset = _adr
            if (_decompress_size == _compress_size):
                m_content.compressed = False
            else:
                m_content.compressed = True
            self.content.append(m_content)
            print("________\n%s \nIndex_pos:%08x\nCompress Size:%d\nDecompress Size:%d\nOFFSET:%08x"%((basename + "\\" + _name), m, _compress_size, _decompress_size,_adr))

        pass

pak = PAK()
pak.Unpack("DATA01.PAC" , "DATA01.PAC_unpacked")
pak = PAK()
pak.Unpack("DATA02.PAC" , "DATA02.PAC_unpacked")
pak = PAK()
pak.Unpack("DATA00.PAC" , "DATA00.PAC_unpacked")

