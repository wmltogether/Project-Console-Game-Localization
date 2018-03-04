# -*- coding:utf-8 -*-
import codecs
import os
import struct
import BinaryHelper
from cStringIO import StringIO
import binascii
from JsonHelper import JsonHelper
import shutil
from shutil import * 

img_folder = "../UNPACK/"
patch_folder = "../PATCH/"
elf_path = "../SLPM_654.62"
fld_path = "../UNPACK/fld/f/bin/FLDALL.TBL"
logger = codecs.open("log.txt", "wb", "utf-8")

class ELFCHUNK:
    def __init__(self):
        self.TEXTLIST = []
class LocText(object):
    def __init__(self):
        self.ELFTAG = ""
        self.TEXT_0_JP = ""
        self.TEXT_1_CN = ""

def FastFixElf(filebuffer, tbl_path ,binaryTable):
    table = GetTable(tbl_path)
    elftable = ELFCHUNK()

    elftable.__dict__ = JsonHelper.Serialize(codecs.open(binaryTable, "rb", "utf-8").read())
    vLocText = LocText()
    for i in xrange(len(elftable.TEXTLIST)):
        vLocText.__dict__ = elftable.TEXTLIST[i]
        offset = int(vLocText.ELFTAG.split(",")[0],16)
        size = int(vLocText.ELFTAG.split(",")[1], 10)
        cnData = TextCore.ConvertTextToData(vLocText.TEXT_1_CN, table)
        if (len(cnData) > size):
            logerror(u"%s 超出范围，默认范围是%d，超出了%d字节"%(vLocText.TEXT_1_CN,size,len(cnData) - size))
        else:
            filebuffer.seek(offset, 0)
            filebuffer.write(cnData)
            filebuffer.write("\x00" * (size - len(cnData)))
    pass


def logerror(strs):
    print(strs)
    
    logger.write(strs + "\r\n")

def GetTable(tbl_name):
    fp = codecs.open(tbl_name, 'rb', 'utf-16')
    lines = fp.readlines()
    base_tbl = {}
    for line in lines:
        if "=" in line:
            code, char = line.split("=")[:2]
            char = char.replace("\r", "")
            char = char.replace("\n", "")
            base_tbl[char] = int(code, 16)
    return base_tbl


def findctr_code(string, original_text):
    if not "}" in string:
        logerror(u"error :[%s] >> } code is missing \n text: [%s]" %
              (string, original_text))
        return ""
    pos = 0
    ctr_str = ""
    mark = 0
    while pos < len(string):
        char = string[pos]
        if char == "{":
            ctr_str += char
            mark = 1
            pos += 1

        elif char == "}":
            ctr_str += char
            break
        else:
            ctr_str += char
            mark = 1
            pos += 1
    return ctr_str[1:-1]


def PreCheckString(string):
    pos = 0
    items = []
    while pos < len(string):
        char = string[pos]
        if char == "{":
            ctr_str = findctr_code(string[pos:], string)
            if ctr_str == "":
                break
            pos += len(ctr_str) + 2
            if (ctr_str in ["start" ]):
            # if (ctr_str in ["start", "f20707ff", "name:1", "format:1", "format:2", "end", "00" ]):
                items.append(ctr_str)
        else:
            pos += 1
    return items


def makestrDict(lines):
    string_list = []
    head_list = []
    strDict = {}
    num = len(lines)
    for index, line in enumerate(lines):
        if u'####' in line:
            head_list.append(line[5:-7])
            i = 1
            string = ''
            while True:
                if index + i >= num:
                    break
                if '####' in lines[index + i]:
                    break
                string += lines[index + i]
                i += 1
            string_list.append(string[:-4])
            strDict[line[5:-7]] = string[:-4]
    return strDict


def makestr(lines):
    string_list = []
    head_list = []
    num = len(lines)
    for index, line in enumerate(lines):
        if u'####' in line:
            head_list.append(line[5:-7])
            i = 1
            string = ''
            while True:
                if index + i >= num:
                    break
                if '####' in lines[index + i]:
                    break
                string += lines[index + i]
                i += 1
            string_list.append(string[:-4])
    return head_list, string_list


def CreateDict(jp_lines, cn_lines, useJP=False):
    new_dict = {}
    jp_dict = makestrDict(jp_lines)
    cn_dict = makestrDict(cn_lines)
    keys = jp_dict.keys()
    for i in xrange(len(keys)):
        mkey = keys[i]
        jp_text = jp_dict[mkey]
        cn_text = ""
        if (mkey in cn_dict):
            cn_text = cn_dict[mkey]
        else:
            cn_text = jp_dict[mkey]
        if (useJP == True):
            jP_ctr_lst = PreCheckString(jp_text)
            cn_ctr_lst = PreCheckString(cn_text)
            if sorted(jP_ctr_lst) != sorted(cn_ctr_lst):
                cn_text = jp_text
            new_dict[mkey] = cn_text
        else:
            new_dict[mkey] = cn_text
    return new_dict


def PreCheck(jp_lines, cn_lines):
    result = True
    jp_dict = makestrDict(jp_lines)
    cn_dict = makestrDict(cn_lines)
    keys = jp_dict.keys()
    for i in xrange(len(keys)):
        mkey = keys[i]
        jp_text = jp_dict[mkey]
        cn_text = ""
        if (mkey in cn_dict):
            cn_text = cn_dict[mkey]
        else:
            cn_text = jp_dict[mkey]
        jP_ctr_lst = PreCheckString(jp_text)
        cn_ctr_lst = PreCheckString(cn_text)
        if sorted(jP_ctr_lst) != sorted(cn_ctr_lst):
            logerror(u"[error] ctr code error ->[jp_text:%s][cn_text:%s]" %
                  (jp_text.encode("cp936", "ignore").decode("cp936", "ignore"), cn_text.encode("cp936", "ignore").decode("cp936", "ignore")))
            result = False
    return result


def createElfPtr(ref_elf_ptr):
    fs = codecs.open("elf_ptr.p.txt", "rb", "utf-16")
    lines = fs.readlines()
    elf_ptr_table = {}
    for line in lines:
        if ("|" in line):
            items = line.split("|")
            _id = items[0]
            if (ref_elf_ptr == items[1].split(",")[0]):
                _code = ",".join(items[1].split(",")[1:])
                elf_ptr_table[_code] = _id
    fs.close()
    return elf_ptr_table


def FindIndex(list0, value):
    try:
        return list0.index(value)
    except:
        return -1


SEQ_BASE_NUM_LOOP = 2
SEQ_FLAG_ODD = 1 << 3
SEQ_BASE = 0x07


class Compress(object):

    def __init__(self, PtrList):
        self.PtrList = PtrList
        self.addressRelocBytes = []
        self.prevRelocSum = 0

    def CompressPtr(self, base_offset=0x20):
        self.prevRelocSum = 0
        sequences = self.DetectAddressSequenceRuns()
        for i in xrange(len(self.PtrList)):
            seqIdx = FindIndex(sequences, i)
            reloc = (self.PtrList[i] - self.prevRelocSum) - base_offset
            if seqIdx != -1:
                self.EncodeReloc(reloc)
                numSeq = sequences[seqIdx].numAddressInSeq - 1
                baseLoopMult = (numSeq - SEQ_BASE_NUM_LOOP) / SEQ_BASE_NUM_LOOP
                isOdd = (numSeq % 2) == 1
                reloc = SEQ_BASE
                reloc |= baseLoopMult << 4
                if (isOdd):
                    reloc |= SEQ_FLAG_ODD
                self.addressRelocBytes.append(struct.pack("B", reloc & 0xff))
                i += numSeq
                self.prevRelocSum += numSeq * 4
            else:
                self.EncodeReloc(reloc)

        return b"".join(self.addressRelocBytes)

    def EncodeReloc(self, reloc):
        if ((reloc & 0x01) == 0):
            newReloc = reloc >> 1
            if (newReloc < 0xff):
                self.addressRelocBytes.append(
                    struct.pack("B", newReloc & 0xff))
            else:
                self.ExtendReloc(reloc)
        else:
            self.ExtendReloc(reloc)
        self.prevRelocSum += reloc
        pass

    def ExtendReloc(self, reloc):
        relocLo = (reloc & 0x00FF) + 1
        relocHi = (reloc & 0xFF00) >> 8
        self.addressRelocBytes.append(struct.pack("B", relocLo & 0xff))
        self.addressRelocBytes.append(struct.pack("B", relocHi & 0xff))
        pass

    def DetectAddressSequenceRuns(self):
        sequences = []
        for i in xrange(len(self.PtrList)):
            if (i + 1 == len(self.PtrList)):
                break
            if (self.PtrList[i + 1] - self.PtrList[i] == 4):
                seq = AddressSequence()
                seq.addrLocationListStartIdx = i
                seq.numAddressInSeq = 2
                i += 1
                while (i + 1 < len(self.PtrList)):
                    if (self.PtrList[i + 1] - self.PtrList[i] == 4):
                        seq.numAddressInSeq += 1
                        i += 1
                    else:
                        break
                if (seq.numAddressInSeq > 2):
                    sequences.append(seq)
        return sequences


class AddressSequence(object):

    def __init__(self):
        self.addrLocationListStartIdx = 0
        self.numAddressInSeq = 0

ASCII_CHARS= u" !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
class TextCore(object):

    @staticmethod
    def ConvertTextToData(string, table):
        string = string.replace("\r", "")
        string = string.replace("\n", "\n")
        hex = ""
        pos = 0
        tmp_ctr = ""
        while pos < len(string):
            char = string[pos]
            if char == "{":
                ctr_str = findctr_code(string[pos:], string)
                items = ctr_str
                items = items.replace(u"\uff1a",":")
                if items == "end":
                    tmp_ctr += struct.pack(">H", 0xf104)
                elif items.lower() == "0d":
                    tmp_ctr += struct.pack("B", 0xd)
                elif items.lower() == "0a":
                    tmp_ctr += struct.pack("B", 0xa)
                elif items == "format:1":
                    tmp_ctr += struct.pack(">I", 0xf20301ff)
                elif items == "format:2":
                    tmp_ctr += struct.pack(">I", 0xf20302ff)
                elif items == "start":
                    tmp_ctr += struct.pack(">I", 0xf208ffff)
                elif items == "name:1":
                    tmp_ctr += struct.pack(">I", 0xf20d01ff)
                elif ":" in items:
                    cd = items.split(":")[0]
                    value = int(items.split(":")[1], 16)
                    if cd == "sp":
                        tmp_ctr += struct.pack(">H", 0xf206)
                        tmp_ctr += struct.pack("B", value)
                        tmp_ctr += struct.pack("B", 0xff)

                    elif cd == "color":
                        tmp_ctr += struct.pack(">H", 0xf202)
                        tmp_ctr += struct.pack("B", value)
                        tmp_ctr += struct.pack("B", 0xff)
                else:
                    v = ""
                    try:
                        v = binascii.a2b_hex(items)
                    except:
                        print("error binascii a2b_hex" + items)
                    tmp_ctr += v
                pos += len(ctr_str) + 2
            else:
                if char == ' ':
                    tmp_ctr += struct.pack("B", 0x20)
                elif char == u"　":
                    tmp_ctr += struct.pack(">H", 0x8080)
                elif char == u"—":
                    tmp_ctr += struct.pack(">H", 0x808d)
                elif char == '\n':
                    tmp_ctr += struct.pack("B", 0x0a)
                elif char in table:
                    tmp_ctr += struct.pack(">H", table[char])
                elif char in ASCII_CHARS:
                    tmp_ctr += (char.encode("ascii"))
                else:
                    logerror(u"error :%s %s is not in tbl" %
                          (char.encode('unicode-escape'),char.encode("cp936", "ignore").decode("cp936", "ignore")))
                pos += 1
        return tmp_ctr


class TextParser(object):

    def __init__(self):
        pass
    def RebuidBF(self, data, tbl_name, cnDict, isELF=False, ref_ptr="null"):
        gsptr = 0
        ms = BinaryHelper. BinaryReader(StringIO(data))
        dst = BinaryHelper.BinaryWriter(StringIO())
        dst.WriteBytes(data)
        dst.Seek(0)
        ms.Seek(0)
        ms.Seek(0x10)
        nums = ms.ReadInt32()
        ms.Seek(0x20)
        dst.Seek(0x20 + 0x10 * nums)
        dst.Truncate()
        for i in xrange(nums):
            ms.Seek(0x20 + 0x10 * i)
            _id = ms.ReadInt32()
            block_unit = ms.ReadInt32()
            block_nums = ms.ReadInt32()
            offset = ms.ReadInt32()
            ms.Seek(offset)
            data = ms.ReadBytes(block_unit * block_nums)
            if data[0x8:0xc] == "MSG1":
                data = self.RebuildBMD(data, tbl_name, cnDict, isELF, ref_ptr)
            dst.Seek(0, 2)
            v_pos = dst.Tell()
            dst.WriteBytes(data)
            if data[0x8:0xc] == "MSG1":
                gsptr = dst.Tell()
            dst.Seek(0x20 + 0x10 * i)
            dst.WriteInt32(_id)
            dst.WriteInt32(block_unit)
            dst.WriteInt32(len(data)/block_unit)
            dst.WriteInt32(v_pos)

        end = ms.base_stream.read()
        dst.Seek(0, 2)
        v_pos = dst.Tell()
        dst.Seek(0, 2)
        dst.WriteBytes(end)
        dst.Seek(4)
        dst.WriteInt32(gsptr)
        dst_data = dst.base_stream.getvalue()
        return dst_data

    def RebuildBMD(self, data, tbl_name, cnDict, isELF=False, ref_ptr = "null"):
        code_ptr_list = []
        if isELF == True:
            elf_ptr_table = createElfPtr(ref_ptr)
        bmd_data_list = []
        bmd_string_list = []
        table = GetTable(tbl_name)
        base_offset = 0x20
        ms = BinaryHelper.BinaryReader(StringIO(data))
        ms.Seek(0)

        dst = BinaryHelper.BinaryWriter(StringIO())
        dst.WriteBytes(data)
        dst.Seek(0)

        unk0 = ms.ReadInt32()
        bmd_size = ms.ReadInt32()
        sig = ms.base_stream.read(4)
        null = ms.ReadInt32()
        code_offset = ms.ReadInt32()
        code_size = ms.ReadInt32()
        index_nums = ms.ReadInt32()
        unk = ms.ReadInt32()

        ms.Seek(code_offset)
        code_data = ms.ReadBytes(code_size)
        ms.Seek(base_offset)
        for i in xrange(index_nums):
            ms.Seek(base_offset + i * 8 + 4)
            code_ptr_list.append(ms.Tell())
        ms.Seek(base_offset + 8 * index_nums)

        code_ptr_list.append(ms.Tell())

        title_data_pos = ms.ReadInt32()
        hasTitle = ms.ReadInt32()
        font_data_pos = ms.ReadInt32()
        null = ms.ReadInt32()
        title_datas = []
        if (hasTitle > 0):
            ms.Seek(title_data_pos + base_offset)
            for i in xrange(hasTitle):
                ms.Seek(title_data_pos + base_offset + 4 * i)
                v_title_pos = ms.ReadInt32()
                ms.Seek(v_title_pos + base_offset)
                title_str = ms.ReadCString()
                title_datas.append(title_str)
        else:
            title_data = ""
        font_data = ""
        if (font_data_pos > 0):
            ms.Seek(font_data_pos + base_offset)
            font_data = ms.ReadBytes(
                code_offset - (font_data_pos + base_offset))

        dst.Seek(base_offset + index_nums * 8 + 0x10, 0)
        dst.Truncate()

        for x in xrange(index_nums):
            ms.Seek(base_offset + 8 * x, 0)
            _id = ms.ReadInt32()

            _offset = ms.ReadInt32()
            _offset = base_offset + _offset
            ms.Seek(_offset)
            code_name_data = ms.ReadBytes(0x18)
            code_name = code_name_data.split("\x00")[0]
            sub_nums0 = ms.ReadInt16()
            sub_nums1 = ms.ReadInt16()
            sub_nums = sub_nums0
            sp = 0
            if sub_nums == 0:
                sp = 1
                null = ms.ReadInt32()
                sub_nums = sub_nums1
            sub_offsets = list(struct.unpack("%dI" %
                                             sub_nums,
                                             ms.base_stream.read(4 * sub_nums)))
            sub_size = ms.ReadInt32() - 1
            sub_offsets.append(sub_offsets[0] + sub_size)

            dst.Seek(0, 2)
            p_pos0 = dst.Tell()

            if (p_pos0 % 4 != 0):
                dst.WriteBytes("\x00" * (4 - p_pos0 % 4))
            p_pos0 = dst.Tell()
            dst.WriteBytes(code_name_data)
            dst.WriteInt16(sub_nums0)
            dst.WriteInt16(sub_nums1)
            if (sp == 1):
                dst.WriteInt32(0)
            p_pos1 = dst.Tell()
            for j in xrange(sub_nums):
                code_ptr_list.append(dst.Tell())
                dst.WriteBytes("\x00" * 4)
            p_pos2 = dst.Tell()
            dst.WriteBytes("\x00" * 4)
            dst.Seek(0, 2)
            tmp_pos1 = dst.Tell()
            for j in xrange(sub_nums):

                c_offset = sub_offsets[j] + base_offset
                c_end = sub_offsets[j + 1] + base_offset
                c_size = c_end - c_offset
                ms.Seek(c_offset)
                c_data = ms.ReadBytes(c_size)
                mKey = "%s,%d,%d" % (code_name,x,j)
                if isELF == True:
                    mKey = elf_ptr_table[mKey]
                if (mKey) in cnDict:
                    cntext = cnDict[mKey]
                    c_data = TextCore.ConvertTextToData (cntext, table)
                dst.Seek(0, 2)
                v_pos = dst.Tell()
                dst.WriteBytes(c_data)
                d_pos = dst.Tell()
                if (d_pos % 4 != 0):
                    dst.WriteBytes("\x00" * (4 - d_pos % 4))
                dst.Seek(p_pos1 + j * 4)
                dst.WriteInt32(v_pos - base_offset)

            dst.Seek(0, 2)
            dst.WriteBytes("\x00")
            tmp_pos2 = dst.Tell()
            if (tmp_pos2 % 4 != 0):
                dst.WriteBytes("\x00" * (4 - tmp_pos2 % 4))
            v_size = tmp_pos2 - tmp_pos1
            dst.Seek(p_pos2)
            dst.WriteInt32(v_size)
            dst.Seek(base_offset + 8 * x + 4)
            dst.WriteInt32(p_pos0 - base_offset)

            pass
        dst.Seek(0, 2)
        title_pos = dst.Tell()
        if hasTitle > 0:
            t_pos_array = []
            dst.WriteBytes("\x00" * 4 * hasTitle)
            for i in xrange(len(title_datas)):
                title_data = title_datas[i]
                mKey = "%s,%d,%d" % ("ACTOR_VAL", i, 0)
                if isELF == True:
                    mKey = elf_ptr_table[mKey]
                if (mKey) in cnDict:
                    cntext = cnDict[mKey]
                    title_data = TextCore.ConvertTextToData(cntext, table)
                t_pos = dst.Tell()
                
                dst.WriteBytes(title_data + "\x00")
                t_pos_array.append(t_pos)
            tmp_pos3 = dst.Tell()
            dst.Seek(title_pos)
            for i in xrange(len(t_pos_array)):
                code_ptr_list.append(dst.Tell())
                dst.WriteInt32(t_pos_array[i] - base_offset)
            dst.Seek(0, 2)
            if (tmp_pos3 % 4 != 0):
                dst.WriteBytes("\x00" * (4 - tmp_pos3 % 4))
        dst.Seek(0, 2)
        font_pos = 0
        if (len(font_data) > 0):
            dst.Seek(0, 2)
            font_pos = dst.Tell()
            dst.WriteBytes(font_data)
        dst.Seek(0, 2)
        v_code_pos = dst.Tell()
        code_data_compressor = Compress(code_ptr_list)
        code_data = code_data_compressor.CompressPtr(0x20)
        dst.WriteBytes(code_data)
        v_bmd_size = dst.Tell()
        dst.Seek(0x4)
        dst.WriteInt32(v_bmd_size)
        dst.Seek(0x10)
        dst.WriteInt32(v_code_pos)
        dst.Seek(0x14)
        dst.WriteInt32(len(code_data))
        dst.Seek(base_offset + index_nums * 8)
        dst.WriteInt32(title_pos - base_offset)
        dst.Seek(base_offset + index_nums * 8 + 8)
        if (font_pos > 0):
            dst.WriteInt32(font_pos - base_offset)
        dst_bmd_data = dst.base_stream.getvalue()
        return dst_bmd_data

def FixKeyboard(table_dict,ELF_BUFFER):
    fs = codecs.open("name_ent_gb2132.txt", "rb", "cp936")
    data = fs.read()
    base_offset = 0x00445bf8
    end_offset = 0x00447778
    ELF_BUFFER.seek(base_offset)
    nums = (end_offset - base_offset) / 2
    p = 0 
    for i in xrange(nums):
        print(hex(base_offset + i* 2))
        ELF_BUFFER.seek(base_offset + i* 2, 0)
        chrt = struct.unpack(">H", ELF_BUFFER.read(2))[0]
        if ((chrt >= 0x83d5) and (chrt < 0x9b00)):
            if (p < len(data)):
                haxchar = data[p]
                p += 1
                if (haxchar in table_dict):
                    ELF_BUFFER.seek(-2,1)
                    ELF_BUFFER.write(struct.pack(">H", table_dict[haxchar]))
                else:
                    ELF_BUFFER.seek(-2,1)
                    ELF_BUFFER.write(struct.pack(">H", 0x8080))

def main():

    textParser = TextParser()
    TBL_PATH = "charlist_making\\ch.TBL"
    table_dict = GetTable(TBL_PATH)
    fl = os.listdir("cn-text")
    ELF_FILE = open(elf_path, "rb")
    ELF_BUFFER = StringIO()
    ELF_BUFFER.write(ELF_FILE.read())
    ELF_BUFFER.seek(0)
    ELF_BUFFER.seek(0x001c887C)
    # 强制逐行扫描
    # ELF_BUFFER.write("\x00\x00\x11\x24")
    # ELF_BUFFER.write("\x05\x00\x12\x24")
    # ELF_BUFFER.write("\x01\x00\x02\x24")
    # 强制自定义输入法编码
    FixKeyboard(table_dict,ELF_BUFFER)
    # 强制重新定义font1编码
    ELF_BUFFER.seek(0x00226340)
    
    base_id = 0x8080
    for i in xrange(2372):
        if (base_id + i)%0x100 == 0:
            base_id += 0x80
        char_id = base_id + i
        ELF_BUFFER.write(struct.pack("H", char_id))
    ELF_BUFFER.seek(0)
    ELF_FILE.close()
    
    FLD_FILE = open(fld_path, "rb")
    FLD_BUFFER = StringIO()
    FLD_BUFFER.write(FLD_FILE.read())
    FLD_BUFFER.seek(0)
    FLD_FILE.close()
    

    FastFixElf(ELF_BUFFER, TBL_PATH, "ELF_HACKS.json")
    FastFixElf(FLD_BUFFER, TBL_PATH, "FIELD_TABLE.json")

    for fn in fl:
        logerror(fn)
        if os.path.exists("jp-text/%s" % fn):
            jp_lines = codecs.open("jp-text/%s" %
                                   fn, "rb", "utf-16").readlines()
            cn_lines = codecs.open("cn-text/%s" %
                                   fn, "rb", "utf-16").readlines()
            if PreCheck(jp_lines, cn_lines) == True:
                cnDict = {}
                cnDict = CreateDict(jp_lines, cn_lines)
            else:
                print("precheck false" + fn)
                cnDict = CreateDict(jp_lines, cn_lines, useJP=True)
            if ("img__" in fn):

                bin_path = (img_folder + fn.replace("img__",
                                                    "").replace("__", "/"))[:-4]
                BIN_FILE = open(bin_path, "rb")
                BIN_DATA = BIN_FILE.read()
                BIN_FILE.close()
                if (bin_path[-3:].lower() == ".bf"):
                    BIN_DATA = textParser.RebuidBF(
                        BIN_DATA, TBL_PATH, cnDict)
                    pass
                elif (bin_path[-4:].lower() == ".bmd"):
                    BIN_DATA = textParser.RebuildBMD(
                        BIN_DATA, TBL_PATH, cnDict)
                    pass
                dst_path = (patch_folder + fn.replace("img__",
                                                      "").replace("__", "/"))[:-4]
                dst_folder = "/".join(dst_path.split("/")[:-1])
                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)
                dst_file = open(dst_path, "wb")
                dst_file.write(BIN_DATA)
                dst_file.close()
            elif "SLPM_654.62_00" in fn:
                s_offset = int(fn.split("SLPM_654.62_")[1][:8], 16)
                ELF_BUFFER.seek(s_offset + 4)
                chunk_size = struct.unpack("I", ELF_BUFFER.read(4))[0]
                ELF_BUFFER.seek(s_offset + 8)
                SIG = ELF_BUFFER.read(4)
                ELF_BUFFER.seek(s_offset)
                ppp = False
                dchunk = ""
                ref_ptr = ("%08x"%s_offset).lower()
                if (SIG == "MSG1"):
                    ppp = True
                    bmd_chunk = ELF_BUFFER.read(chunk_size)
                    dchunk = textParser.RebuildBMD(
                        bmd_chunk, TBL_PATH, cnDict, True, ref_ptr)
                elif (SIG == "FLW0"):
                    ppp = True
                    bmd_chunk = ELF_BUFFER.read(chunk_size)
                    dchunk = textParser.RebuidBF(
                        bmd_chunk, TBL_PATH, cnDict, True, ref_ptr)
                if (ppp):
                    if (len(dchunk) <= chunk_size):
                        ELF_BUFFER.seek(s_offset)
                        ELF_BUFFER.write(dchunk)
                        ELF_BUFFER.write("\x00" * (chunk_size - len(dchunk)))
                    else:
                        vlen = len(dchunk)-chunk_size
                        pps = open("ELF_TMP//%08x_cn.bin"%s_offset, "wb")
                        pps.write(dchunk)
                        pps.close()
                        ppo = open("ELF_TMP//%08x_jp.bin"%s_offset, "wb")
                        ppo.write(bmd_chunk)
                        ppo.close()
                        
                        logerror(u"Error:[%s] ELF CHUNK 超出容量 [%08x]字节，需要缩减至少[%d]个汉字" %(fn, vlen,  vlen/2))
                pass
                
    dst = open(patch_folder + "SLPM_654.62", "wb")
    dst.write(ELF_BUFFER.getvalue())
    dst.close()
    
    font0Data = open("./charlist_making/font0_ch.fnt", "rb").read()
    font1Data = open("./charlist_making/font1_ch.fnt", "rb").read()
    fontentData = open("./charlist_making/name_ent_ch.fnt", "rb").read()
    
    if not os.path.exists(patch_folder + "/font/"):
        os.makedirs(patch_folder + "/font/")
        
    font0 = open(patch_folder + "/font/" + "font0.fnt", "wb")
    font0.write(font0Data)
    font0.close()
    
    font1 = open(patch_folder + "/font/" + "font1.fnt", "wb")
    font1.write(font1Data)
    font1.close()
    
    name_ent = open(patch_folder + "/font/" + "name_ent.fnt", "wb")
    name_ent.write(fontentData)
    name_ent.close()
    
    if not os.path.exists(patch_folder + "/fld/f/bin/"):
        os.makedirs(patch_folder + "/fld/f/bin/")
    fld_table = open(patch_folder + "/fld/f/bin/" + "FLDALL.TBL", "wb")
    fld_table.write(FLD_BUFFER.getvalue())
    fld_table.close()
    
    shutil.copyfile( patch_folder +"/SLPM_654.62", "../IMPORT/SLPM_654.62")
    pass

if __name__ == "__main__":
    main()
