# -*- coding: utf-8 -*-
import codecs
import os
import struct
from cStringIO import StringIO


def GetTable(tbl_name):
    fp = codecs.open(tbl_name, 'rb', 'utf-16')
    lines = fp.readlines()
    base_tbl = {}
    for line in lines:
        if "=" in line:
            code, char = line.split("=")[:2]
            char = char.replace("\r", "")
            char = char.replace("\n", "")
            base_tbl[int(code, 16)] = char
    return base_tbl


def GetFiles(adr):
    dirlst = []
    for root, dirs, files in os.walk(adr):
        for name in files:
            adrlist = os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst


class BinaryReader:

    def __init__(self, base_stream):
        self.base_stream = base_stream

    def seek(self, position, region=0):
        self.base_stream.seek(position, region)

    def ReadByte(self):
        return self.base_stream.read(1)

    def read(self, count):
        return self.base_stream.read(count)

    def ReadBytes(self, count):
        return self.base_stream.read(count)

    def ReadInt16(self):
        return struct.unpack('H', self.base_stream.read(2))[0]

    def ReadInt32(self):
        return struct.unpack('i', self.base_stream.read(4))[0]

    def ReadUInt32(self):
        return struct.unpack('I', self.base_stream.read(4))[0]

    def ReadInt64(self):
        return struct.unpack('Q', self.base_stream.read(8))[0]

    def ReadString(self):
        s = ""
        while True:
            c = self.ReadByte()
            if ord(c) == 0:
                self.base_stream.seek(-1, 1)
                break
            else:
                s += c
        return s


class TextParser(object):

    def Data2Text(self, c_data, table):
        tmp = StringIO(c_data)
        tmp.seek(0)
        pos = 0
        current_string = u""
        while pos < len(c_data):
            v0 = ord(tmp.read(1))
            if v0 == 0xf1:
                v1 = ord(tmp.read(1))
                if (v0, v1) == (0xf1, 0x04):
                    current_string += u"{end}"
                else:
                    current_string += u"{%02x%02x}" % (
                        v0, v1)
                pos += 2
            elif v0 == 0xf2:
                # code
                v1 = ord(tmp.read(1))
                v2 = ord(tmp.read(1))
                v3 = ord(tmp.read(1))
                pos += 4
                if (v0, v1, v2, v3) == (0xf2, 0x03, 0x01, 0xff):
                    current_string += u"{format:1}"

                elif (v0, v1, v2, v3) == (0xf2, 0x03, 0x02, 0xff):
                    current_string += u"{format:2}"

                elif (v0, v1, v2, v3) == (0xf2, 0x0d, 0x01, 0xff):
                    current_string += u"{name:1}"

                elif (v0, v1, v3) == (0xf2, 0x06, 0xff):
                    current_string += u"{sp:%d}" % v2

                elif (v0, v1, v3) == (0xf2, 0x02, 0xff):
                    current_string += u"{color:%d}" % v2

                elif (v0, v1, v2, v3) == (0xf2, 0x08, 0xff, 0xff):
                    current_string += u"{start}"
                else:
                    current_string += u"{%02x%02x%02x%02x}" % (
                        v0, v1, v2, v3)
            elif v0 == 0xc0:
                v1 = ord(tmp.read(1))
                current_string += u"{%02x%02x}" % (
                    v0, v1)
                pos += 2
            elif v0 >= 0xf3:
                print("%x" % v0)
            elif 0x80 <= v0 < 0xf0:
                # full jis
                v1 = ord(tmp.read(1))
                if (v0 * 0x100 + v1) in table:
                    current_string += table[(v0 * 0x100 + v1)]
                else:
                    print("code :%04x not in table" %
                          ((v0 * 0x100 + v1)))
                pos += 2

            elif (v0 >= 0x20 and v0 <= 0x7e):
                # ascii
                current_string += chr(v0)
                pos += 1
            elif v0 == 0x0a:
                # cr lf
                current_string += "\r\n"
                pos += 1
            else:
                current_string += "{%02x}" % v0
                pos += 1
        return current_string

    def ParseBMD(self, data, tbl_name="jp_bmd.TBL"):
        bmd_data_list = []
        bmd_string_list = []
        table = GetTable(tbl_name)
        base_offset = 0x20
        ms = BinaryReader(StringIO(data))
        ms.seek(0)
        unk0 = ms.ReadInt32()
        bmd_size = ms.ReadInt32()
        sig = ms.base_stream.read(4)
        null = ms.ReadInt32()
        code_offset = ms.ReadInt32()
        code_size = ms.ReadInt32()
        index_nums = ms.ReadInt32()
        unk = ms.ReadInt32()
        for x in xrange(index_nums):
            ms.seek(base_offset + 8 * x, 0)
            #print("read :%08x(%x)"%((base_offset + 8 * x), index_nums))
            _id = ms.ReadInt32()
            _offset = ms.ReadInt32()
            _offset = base_offset + _offset
            ms.seek(_offset)
            # print(hex(ms.base_stream.tell()))
            code_name = ms.ReadBytes(0x18)
            code_name = code_name.split("\x00")[0]
            # print(hex(ms.base_stream.tell()))
            sub_nums = ms.ReadInt16()
            sub_nums1 = ms.ReadInt16()
            if sub_nums == 0:
                null = ms.ReadInt32()
                sub_nums = sub_nums1
            # print(hex(sub_nums))
            sub_offsets = list(struct.unpack("%dI" %
                                             sub_nums,
                                             ms.base_stream.read(4 * sub_nums)))
            sub_size = ms.ReadInt32() - 1
            sub_offsets.append(sub_offsets[0] + sub_size)

            for j in xrange(sub_nums):
                c_offset = sub_offsets[j] + base_offset
                c_end = sub_offsets[j + 1] + base_offset
                c_size = c_end - c_offset
                ms.seek(c_offset)
                #print("%08x , %x"%(c_offset, c_size))
                c_data = ms.read(c_size)
                current_string = self.Data2Text(c_data, table)
                bmd_string_list.append((code_name,x, j, current_string))
        ms.seek(base_offset + 8 * index_nums,0)
        actorChunkOffset = ms.ReadInt32()
        actorNums = ms.ReadInt32()
        for x in xrange(actorNums):
            ms.seek(actorChunkOffset + base_offset + 4 * x, 0)
            _offset = ms.ReadInt32()
            _offset = base_offset + _offset
            ms.seek(_offset)
            actorData  = ms.ReadString()
            current_string = self.Data2Text(actorData, table)
            bmd_string_list.append(("ACTOR_VAL",x , 0, current_string))
        return bmd_string_list

    def ParseBF(self, data, tbl_name="jp_bmd.TBL"):
        ms = BinaryReader(StringIO(data))
        ms.seek(0)
        ms.seek(0x10)
        nums = ms.ReadInt32()
        ms.seek(0x20)
        s = 0
        bmd_string_list = []
        for i in xrange(nums):
            ms.seek(0x20 + 0x10 * i)
            _id = ms.ReadInt32()
            array_nums = ms.ReadInt32()
            size = ms.ReadInt32()
            offset = ms.ReadInt32()
            ms.seek(offset)
            data = ms.ReadBytes(size * array_nums)
            if data[0x8:0xc] == "MSG1":
                print("GOT MSG1--%d"%i)
                s += 1
                bmd_string_list = self.ParseBMD(data,tbl_name)
                return bmd_string_list
        return bmd_string_list

    def ExportText(self, input_folder, dest_folder):
        fl = GetFiles(input_folder)
        for fn in fl:
            if fn[-4:].lower() == ".bmd":
                print(fn)
                fp = open(fn, "rb")
                data = fp.read()
                bmd_string_list = self.ParseBMD(data)
                dest_name = fn.replace("\\", "__")[11:]
                dest = codecs.open(
                    "%s//img__%s.txt" % (dest_folder,
                                    dest_name), "wb", "utf-16")
                for (code, i,j, string) in bmd_string_list:
                    dest.write("#### %s,%d,%d ####\r\n%s\r\n\r\n" %
                               (code, i,j, string))
                fp.close()

            if fn[-3:].lower() == ".bf":
                print(fn)
                fp = open(fn, "rb")
                data = fp.read()
                bmd_string_list = self.ParseBF(data)
                fp.close()

                dest_name = fn.replace("\\", "__")[11:]
                dest = codecs.open(
                    "%s//img__%s.txt" % (dest_folder,
                                    dest_name), "wb", "utf-16")
                for (code, i,j, string) in bmd_string_list:
                    dest.write("#### %s,%d,%d ####\r\n%s\r\n\r\n" %
                               (code, i,j , string))
                fp.close()
        pass

    def SearchELF(self, elf_name):
        data_list = []
        fp = open(elf_name, "rb")
        dsize = os.path.getsize(elf_name)
        pos = 0x002279B0
        fp.seek(pos)
        while pos < (dsize - 0xc):
            tmp_pos = fp.tell()
            data = fp.read(0xc)
            if (data[0:4] == "\x00\x00\x00\x00" and data[-4:] == "FLW0"):
                fsize = struct.unpack("I", data[4:8])[0]
                if (fsize % 4 != 0):
                    mod = 4 - fsize % 4
                print("GOT ELF :%08x, %08X" % (tmp_pos, fsize))
                data_list.append((tmp_pos, fsize))
                fp.seek(tmp_pos, 0)
                fp.seek(fsize, 1)
                fp.seek(mod, 1)
                pos = fp.tell()
            if (data[0:4] == "\x07\x00\x00\x00" and data[-4:] == "MSG1"):
                fsize = struct.unpack("I", data[4:8])[0]
                mod = 0
                if (fsize % 4 != 0):
                    mod = 4 - fsize % 4
                print("GOT ELF :%08x, %08X" % (tmp_pos, fsize))
                data_list.append((tmp_pos, fsize))
                fp.seek(tmp_pos, 0)
                fp.seek(fsize, 1)
                fp.seek(mod, 1)
                pos = fp.tell()
            else:
                fp.seek(-8, 1)
                pos = fp.tell()
        fp.close()
        return data_list

    def ExportELF(self, input_elf, output_folder):
        special_list = [0x002e9c58,0x002f55e8,0x002f9e28,0x002fa080,0x00427680]  # special bmd using font1.tbl
        data_list = self.SearchELF("../" + input_elf)
        fp = open("../" + input_elf, "rb")

        dp = codecs.open(
            "elf_ptr.p.txt", "wb", "utf-16")
        s = 0
        for (offset, size) in data_list:
            fp.seek(offset)
            data = fp.read(size)
            sig = data[0x8:0xc]
            if (sig == "FLW0"):
                print(hex(offset))
                tbl_name = "jp_bmd.TBL"
                bmd_string_list = self.ParseBF(data, tbl_name)
                
            elif (sig == "MSG1"):
                if offset in special_list:
                    tbl_name = "font1.TBL"
                    bmd_string_list = self.ParseBMD(data, tbl_name)
                else:
                    tbl_name = "jp_bmd.TBL"
                    bmd_string_list = self.ParseBMD(data, tbl_name)
            else:
                print(sig)
            dest = codecs.open("%s//%s_%08x_%s.txt" % (output_folder,
                                     input_elf, offset, sig), "wb", "utf-16")
            for (code, i,j, string) in bmd_string_list:
                s += 1
                dest.write("#### %d ####\r\n%s\r\n\r\n" %
                           (s, string))
                dp.write("%d|%08x,%s,%d,%d|\r\n" % (s, offset, code, i, j))

            dest.close()
        dp.close()

        pass
tr = TextParser()
tr.ExportText("../UNPACK", "./jp-text")
tr.ExportELF("SLPM_654.62", "./jp-text")
