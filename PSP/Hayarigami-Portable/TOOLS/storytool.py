import codecs,os,struct
from cStringIO import StringIO

class StoryCode:
    @staticmethod
    def __init__(self):
        self.CODELIST = []
        pass


class StoryParse(object):
    def __init__(self):
        self.storydict = {}
        self.storylist = []
        self.storynums = 0
        self.base_offset = 0
        self.packsize = 0
        self.basename = ""
        self.dest_clear = None


    def GetStoryList(self , fn):
        self.basename = os.path.basename(fn)
        self.packsize = os.path.getsize(fn)
        fp = open(fn , "rb")
        self.base_offset = struct.unpack("I" , fp.read(4))[0]
        self.storynums = struct.unpack("I" , fp.read(4))[0]
        for i in xrange(self.storynums):
            _cnt_id , _cnt_offset = struct.unpack("2I" , fp.read(8))
            self.storylist.append(_cnt_id)
            self.storydict[_cnt_id] = _cnt_offset
        fp.close()

    def _unpack_dat(self , fn):
        self.GetStoryList( fn)
        fp = open(fn , "rb")
        for _cnt_id in self.storylist:
            self.ParseBlock(_cnt_id , fp)

    def decrypt_code(self , string):
        ns = ""
        for s in string:
            ns += chr(ord(s) ^ 0xff)
        return ns

    def FixedWrite(self , buffer , string , pos , fwrite=False):
        sig = ord(string[0])
        if (sig == 0xff):
            # is <>
            if (ord(string[1]) ^ 0xff == 0xf9 and ord(string[2]) ^ 0xff == 0x33):
                var = struct.unpack("%dB"%len(string) , string)
                buffer.write("<pause:")
                for v in var:
                    buffer.write("%02x,"%v)
                buffer.write(">")
            elif (ord(string[1]) ^ 0xff == 0xf9 and ord(string[2]) ^ 0xff == 0x36):
                var = struct.unpack("%dB"%len(string) , string)
                buffer.write("<wait:")
                for v in var:
                    buffer.write("%02x,"%v)
                buffer.write(">")
            elif (ord(string[1]) ^ 0xff == 0xfb and ord(string[2]) ^ 0xff == 0x3b):
                var = struct.unpack("%dB"%len(string) , string)
                buffer.write("<end:")
                for v in var:
                    buffer.write("%02x,"%v)
                buffer.write(">\r\n")
            elif (ord(string[2]) ^ 0xff == 0x2f and ord(string[3]) ^ 0xff == 0xff):
                # shang biao kai shi
                var = struct.unpack("%dB"%len(string) , string)
                buffer.write("<up:")
                for v in var:
                    buffer.write("%02x,"%v)
                buffer.write(">\r\n")

            elif (ord(string[2]) ^ 0xff == 0x2e and ord(string[3]) ^ 0xff == 0xff):
                # shang biao jie shu
                var = struct.unpack("%dB"%len(string) , string)
                buffer.write("</up:")
                for v in var:
                    buffer.write("%02x,"%v)
                buffer.write(">")

            elif (ord(string[2])  == 0x23 and ord(string[3]) == 0x03):
                # she ding ren ming
                buffer.write("<name:")
                buffer.write("%02x,"%ord(string[4]))
                self.dest_clear.write(u"%08x,%d,%s\r\n\r\n"%(pos+5 , len(string[5:-1]),self.decrypt_code(string[5:-1]).decode("cp932")))
                buffer.write("(text|%08x|%d)"%(pos+5,len(string[5:-1])))
                buffer.write(">\r\n")

            elif (ord(string[2])  == 0x79 and ord(string[3]) == 0x05):
                # denglu ci tiao
                var = struct.unpack("%dB"%len(string[:8]) , string[:8])
                buffer.write("<word:")
                for v in var:
                    buffer.write("%02x,"%v)
                #pos = 0
                c1 = string[8:-2]
                self.dest_clear.write(u"%08x,%d,%s\r\n\r\n"%(pos+8 , len(c1),self.decrypt_code(c1).decode("cp932")))
                buffer.write("(text|%08x|%d)"%(pos+8 , len(c1)))
                buffer.write(">")
                
            elif (ord(string[2])  == 0xe9 and ord(string[3]) == 0x03):
                # label
                var = struct.unpack("%dB"%len(string[:0xc]) , string[:0xc])
                buffer.write("<label:")
                for v in var:
                    buffer.write("%02x,"%v)
                #pos = 0
                c1 = string[0xc:-1]
                self.dest_clear.write(u"%08x,%d,%s\r\n\r\n"%(pos+8 , len(c1),self.decrypt_code(c1).decode("cp932")))
                buffer.write("(text|%08x|%d)"%(pos+8 , len(c1)))
                buffer.write(">")

            else:
                var = struct.unpack("%dB"%len(string) , string)
                buffer.write("<code:")
                for v in var:
                    buffer.write("%02x,"%v)
                buffer.write(">\r\n")
        elif sig == 0x00:
            buffer.write("<null>\r\n")

        else:
            if fwrite == False:
                self.dest_clear.write("%08x,%d,%s\r\n\r\n"%(pos , len(string), string.decode("cp932")))
                buffer.write("<text:%08x,%d>"%(pos ,len(string)))
                buffer.write("\r\n")
            else:
                for s in string:
                    buffer.write("<%02x>"%s)


    def ParseBlock(self , _block_id , fp):
        dest = codecs.open("p\\%s_%08d.txt"%(self.basename,_block_id) , "wb" , "utf-16")
        self.dest_clear = codecs.open("jp-text\\%s_%08d.txt"%(self.basename,_block_id) , "wb" , "utf-16")
        _cnt_offset = self.storydict[ _block_id]
        _tmp_list = []
        for v in self.storylist:
            v = self.storydict[v]
            if not v == _cnt_offset:
                _tmp_list.append(v)
        _tmp_list.append(self.packsize)
        fp.seek(_cnt_offset)
        pos = _cnt_offset
        while (pos in _tmp_list) == False:
            _current_char = fp.read(1)
            print(hex(pos))
            if ord(_current_char) == 0xff:
                _method_len = ord(fp.read(1))
                fp.seek(pos)
                _method_data = fp.read(_method_len)
                self.FixedWrite(dest , _method_data , pos)
                pos = fp.tell()
            elif ord(_current_char) == 0x00:
                self.FixedWrite(dest , "\x00", pos)
                pos = fp.tell()

            elif ((ord(_current_char) ^ 0xff) in range(0x20,0x7f)) or ((ord(_current_char) ^ 0xff) in range(0x81,0xfc)):
                #is text
                cpos = pos
                text = chr(ord(_current_char) ^ 0xff)
                while True:
                    c1 = fp.read(1)
                    if ord(c1) in [0x0,0xff]:
                        fp.seek(-1,1)
                        pos = fp.tell()
                        break
                    else:
                        text += chr(ord(c1) ^ 0xff)
                self.FixedWrite(dest , text , cpos)
                pass

            else:
                self.FixedWrite(dest , _current_char, pos , fwrite=True)
                pos = fp.tell()

        pass


sf = StoryParse()
sf._unpack_dat("STORY.DAT")
