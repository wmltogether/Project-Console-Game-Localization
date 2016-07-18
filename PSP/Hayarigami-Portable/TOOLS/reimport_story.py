# -*- coding: utf-8 -*-
import codecs,os,struct
from cStringIO import StringIO
import re
class StoryParse(object):
    def __init__(self):
        self.storydict = {}
        self.storylist = []
        self.storynums = 0
        self.base_offset = 0
        self.packsize = 0
        self.basename = ""
        self.dest_clear = None
        self.mRegexLink = re.compile("\\<.+?\\>")
        self.char_table = self.GetTable()


    def GetTable(self):
        fp = codecs.open("base.TBL",'rb','utf-16')
        fp2 = codecs.open("ch.TBL",'rb','utf-16')
        lines = fp.readlines() + fp2.readlines()
        base_tbl = {}
        for line in lines:
            if "=" in line:
                code,char = line.split("=")[:2]
                char = char.replace("\r" , "")
                char = char.replace("\n" , "")
                base_tbl[char] = int(code,16)
        self.char_table = base_tbl
        return base_tbl

    def GetWQSGDict(self ,lines):
        dict = {}
        for v in lines:
            if "," in v:
                _offset = int(v.split(",")[0],16)
                _len = int(v.split(",")[1],10)
                string = ",".join(v.split(",")[2:])
                string = string.replace("\r" , "")
                string = string.replace("\n" , "")
                string = string.replace("\r" , "")
                string = string.replace(u"(上)" , u"㊤")
                string = string.replace(u"(中)" , u"㊥")
                string = string.replace(u"(下)" , u"㊦")
                string = string.replace(u"(左)" , u"㊧")
                string = string.replace(u"(右)" , u"㊨")
                dict[(_offset ,_len)] = string
        return dict

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

    def _repack_dat(self , original_fn , dest_fn):
        self.GetStoryList(original_fn)
        buffer = StringIO()
        buffer.seek(0)
        buffer.write(struct.pack("I" , self.storynums * 8 + 8))
        buffer.write(struct.pack("I" , self.storynums))
        for i in xrange(self.storynums):
            buffer.write(struct.pack("I" , self.storylist[i]))
            buffer.write(struct.pack("I" , 0))
        base_pos = buffer.tell()
        for i in xrange(self.storynums):
            _cnt_id = self.storylist[i]
            data = self.buildBlock(_cnt_id)
            buffer.seek(0,2)
            tmp_pos = buffer.tell()
            buffer.write(data)
            buffer.seek(8 + 4 + i * 8)
            buffer.write(struct.pack("I" , tmp_pos))
            buffer.seek(0,2)
        dest = open(dest_fn , "wb")
        dest.write(buffer.getvalue())
        dest.close()

    def ParseCode(self , string , ch_dict , jp_dict):
        if "null" in string:
            return ""
        v = string.split(":")[1].split(">")[0]
        l0 = v.split(",")
        buffer = StringIO()
        if "name" in string:
            buffer.write(struct.pack("B", 0xff))
            buffer.write(struct.pack("B", 0x00))
            buffer.write(struct.pack("B", 0x23))
            buffer.write(struct.pack("B", 0x03))
            buffer.write(struct.pack("B", int(l0[0] , 16)))
            if "|" in l0[1]:
                var = l0[1]
                _offset = int(var[1:-1].split("|")[1],16)
                _len = int(var[1:-1].split("|")[2],10)
                if (_offset ,_len) in ch_dict:
                    _str = ch_dict[(_offset , _len)]
                else:
                    _str = jp_dict[(_offset , _len)]
                for char in _str:
                    s = self.char_table[char]

                    if s <= 0xff:
                        s = s ^ 0xff
                        buffer.write(struct.pack("B", s))
                    else:
                        s = s ^ 0xffff
                        buffer.write(struct.pack(">H", s))
            buffer.write(struct.pack("B", 0))
            end_pos = buffer.tell()
            buffer.seek(1)
            buffer.write(struct.pack("B", end_pos))
            return buffer.getvalue()
        elif "label" in string:
            for var in l0:
                if not "|" in var:
                    if len(var) > 0:
                        buffer.write(struct.pack("B", int(var,16)))
                else:
                    _offset = int(var[1:-1].split("|")[1],16)
                    _len = int(var[1:-1].split("|")[2],10)
                    if (_offset ,_len) in ch_dict:
                        _str = ch_dict[(_offset , _len)]
                    else:
                        _str = jp_dict[(_offset , _len)]
                    for char in _str:
                        s = self.char_table[char]
                        if s <= 0xff:
                            s = s ^ 0xff
                            buffer.write(struct.pack("B", s))
                        else:
                            s = s ^ 0xffff
                            buffer.write(struct.pack(">H", s))
            buffer.write(struct.pack("B", 0))
            buffer.write(struct.pack("B", 0))
            end_pos = buffer.tell()
            buffer.seek(1)
            buffer.write(struct.pack("B", end_pos))
            return buffer.getvalue()
        elif "word" in string:
            for var in l0:
                if not "|" in var:
                    if len(var) > 0:
                        buffer.write(struct.pack("B", int(var,16)))
                else:
                    _offset = int(var[1:-1].split("|")[1],16)
                    _len = int(var[1:-1].split("|")[2],10)
                    if (_offset ,_len) in ch_dict:
                        _str = ch_dict[(_offset , _len)]
                    else:
                        _str = jp_dict[(_offset , _len)]
                    for char in _str:
                        s = self.char_table[char]
                        if s <= 0xff:
                            s = s ^ 0xff
                            buffer.write(struct.pack("B", s))
                        else:
                            s = s ^ 0xffff
                            buffer.write(struct.pack(">H", s))
            buffer.write(struct.pack("B", 0))
            buffer.write(struct.pack("B", 0))
            end_pos = buffer.tell()
            buffer.seek(1)
            buffer.write(struct.pack("B", end_pos))
            return buffer.getvalue()
        elif "text" in string:
            _offset = int(l0[0],16)
            _len = int(l0[1],10)
            if (_offset ,_len) in ch_dict:
                _str = ch_dict[(_offset , _len)]
            else:
                _str = jp_dict[(_offset , _len)]
            for char in _str:
                if not char in self.char_table:
                    print(char)
                    print(string)
                s = self.char_table[char]
                if s <= 0xff:
                    s = s ^ 0xff
                    buffer.write(struct.pack("B", s))
                else:
                    s = s ^ 0xffff
                    buffer.write(struct.pack(">H", s))
            return buffer.getvalue()
        else:
            for var in l0:
                if not "|" in var:
                    if len(var) > 0:
                        buffer.write(struct.pack("B", int(var,16)))
            return buffer.getvalue()


    def buildBlock(self , _cnt_id):
        print("p\\%s_%08d.txt"%(self.basename , _cnt_id))
        fp = codecs.open("p\\%s_%08d.txt"%(self.basename , _cnt_id) ,"rb" , "utf-16" )
        chdict = {}
        jpdict = {}
        if os.path.exists("cn-text\\%s_%08d.txt"%(self.basename , _cnt_id)):
            cnfile = codecs.open("cn-text\\%s_%08d.txt"%(self.basename , _cnt_id) ,"rb" , "utf-16" ).readlines()
            chdict = self.GetWQSGDict(cnfile)
        if os.path.exists("jp-text\\%s_%08d.txt"%(self.basename , _cnt_id)):
            jpfile = codecs.open("jp-text\\%s_%08d.txt"%(self.basename , _cnt_id) ,"rb" , "utf-16" ).readlines()
            jpdict = self.GetWQSGDict(jpfile)
        block = StringIO()

        for line in fp.readlines():
            if self.mRegexLink.match(line):
                matcher = self.mRegexLink.findall(line)
                for item in matcher:
                    data = self.ParseCode( item , chdict , jpdict)
                    block.write(data)
                    # special align to 4bytes
                    if (len(data)%4 != 0):block.write("\x00" * (8 - len(data)%4))
                    
        data = block.getvalue()
        return data


fs = StoryParse()
fs._repack_dat("STORY.DAT" , "import\\STORY.DAT")
