import codecs,os,struct
from cStringIO import StringIO

class FileParse(object):
    def __init__(self):
        self.filedict = {}
        self.filelist = []
        self.filenums = 0
        self.base_offset = 0
        self.packsize = 0
        self.basename = ""

    def GetFileList(self , fn):
        self.basename = os.path.basename(fn)
        self.packsize = os.path.getsize(fn)
        fp = open(fn , "rb")
        self.base_offset = 0
        self.filenums = struct.unpack("I" , fp.read(4))[0]
        for i in xrange(self.filenums):
            _cnt_id , _cnt_offset = struct.unpack("2I" , fp.read(8))
            self.filelist.append(_cnt_id)
            self.filedict[_cnt_id] = _cnt_offset
        fp.close()

    def decrypt_code(self , string):
        ns = ""
        for s in string:
            ns += chr(ord(s) ^ 0xff)
        return ns

    def _unpack_dat(self , fn):
        self.GetFileList(fn)
        fp = open(fn , "rb")
        for _cnt_id in self.filelist:
            self.ParseBlock(_cnt_id , fp)

    def DecryptAndDecode(self , string ,codings):
        string = self.decrypt_code(string)
        return string.decode(codings)

    def FixedWrite(self , buffer , string , pos , fwrite=False):
        print(hex(pos))
        sig = ord(string[0])
        if sig == 0x00:
            buffer.write("<00>\r\n")
        else:
            if fwrite == False:
                buffer.write("<text:%08x,%d>"%(pos ,len(string)))
                self.dest_clear .write("%08x,%d,%s\r\n\r\n"%(pos , len(string),self.DecryptAndDecode(string , "cp932")))
                buffer.write("\r\n")
            else:
                for s in string:
                    buffer.write("<%02x>"%ord(s))


    def ParseBlock(self , _block_id , fp):
        dest = codecs.open("p\\%s_%08d.txt"%(self.basename,_block_id) , "wb" , "utf-16")
        self.dest_clear = codecs.open("jp-text\\%s_%08d.txt"%(self.basename,_block_id) , "wb" , "utf-16")
        _cnt_offset = self.filedict[_block_id]
        _tmp_list = []
        for v in self.filelist:
            v = self.filedict[v]
            if not v == _cnt_offset:
                _tmp_list.append(v)

        _tmp_list.append(int(self.packsize))
        fp.seek(_cnt_offset)
        pos = _cnt_offset
        while pos not in _tmp_list:
            _current_char = fp.read(1)
            if ((ord(_current_char) ^ 0xff) in range(0x20,0x7f)) or ((ord(_current_char) ^ 0xff) in range(0x81,0xea)):
                cpos = pos
                text = _current_char
                s = False
                l0 = "\x00"
                while True:
                    c1 = fp.read(1)
                    if (ord(c1)^0xff in range(0x40,0xfd)) and (ord(l0)^0xff in range(0x81,0xfc)):
                        s = True
                    if (ord(c1) in [0x0,0xff]):
                        fp.seek(-1,1)
                        pos = fp.tell()
                        break
                    else:
                        l0 = c1
                        text += c1
                if s == True:
                    self.FixedWrite(dest , text , cpos)
                else:
                    self.FixedWrite(dest , text , cpos , fwrite=True)
                pass

            elif ord(_current_char) == 0x00:
                self.FixedWrite(dest , "\x00", pos , fwrite=True)
                pos = fp.tell()
            else:
                self.FixedWrite(dest , _current_char, pos , fwrite=True)
                pos = fp.tell()
        dest.close()


fs = FileParse()
fs._unpack_dat("OCCULTFILE.DAT")








