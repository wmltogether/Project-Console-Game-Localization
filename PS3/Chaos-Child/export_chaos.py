# -*- coding:utf-8 -*-
import codecs
import os
import glob
import struct
def getTable():
    table_name = u"自定义编码.txt"
    fp = codecs.open(table_name , 'rb' , 'utf-16')
    lines = fp.readlines()
    table_dict = {}
    for line in lines:
        if "=" in line:
            line = line.replace("\r" , "")
            line = line.replace("\n" , "")
            code = int((line.split("=")[0]).upper() ,16)
            char = '='.join(line.split("=")[1:])
            table_dict[code] = char
    fp.close()
    return table_dict
#getTable()
def export_text(filename):
    table_dict = getTable()
    END_CTR = 0xff
    NAME_START = 0x1
    NAME_END = 0x2
    PAGE_END = 0x3
    CR_CODE = 0x0
    COLOR_CODE = 0x4
    JIS_CODE = 0x80
    m_code = 0x0
    fp = open(filename , 'rb' )
    if not os.path.exists('jp-textA'):os.makedirs('jp-textA')
    dest = codecs.open('jp-textA/%s.txt'%filename.split("\\")[-1] , 'wb' , 'utf-16')
    sig = fp.read(4)
    MAGIC_SC3 = '\x53\x43\x33\x00'
    if sig != MAGIC_SC3:
        fp.close()
        print("not a SC3 script :%s"%filename)
        return None
    index_offset , tstart_offset = struct.unpack("2I" , fp.read(8))
    pos = index_offset
    while pos < tstart_offset:
        fp.seek(pos)
        toffset ,  = struct.unpack('I' , fp.read(4))
        pos += 4
        fp.seek(toffset)
        string_buffer = u""
        tmp_ctr = 0
        # print(hex(toffset))
        while True:
            m_byte = fp.read(1)
            m_code = ord(m_byte)
            tmp_ctr += 1
            if JIS_CODE <= m_code <= JIS_CODE + 0x1c:
                second_letter = ord(fp.read(1))
                char_code = m_code * 0x100 + second_letter
                if char_code in table_dict:
                    string_buffer += table_dict[char_code]
                else:
                    string_buffer += u"{%02x}{%02x}"%(m_code , second_letter)
            elif m_code == COLOR_CODE:
                second_letter = ord(fp.read(1))
                third_letter = ord(fp.read(1))
                fourth_letter = ord(fp.read(1))
                string_buffer += u"{%02x}{%02x}{%02x}{%02x}"%(m_code , second_letter , third_letter , fourth_letter)
            elif m_code == PAGE_END:
                string_buffer += u"{%02x}"%(m_code)
            elif m_code == END_CTR and tmp_ctr > 1:
                # tmp_ctr > 1 防止字符串首字节为FF时导出终止
                break
            else:
                string_buffer += u"{%02x}"%(m_code)
        #这里我写错了，pos应该是pos - 4
        dest.write("#### %08x ####\r\n%s\r\n\r\n"%(pos , string_buffer))
        # print(string_buffer.encode("utf-8"))
    dest.close()
    fp.close()
def main():
    fl = glob.iglob('script.cpk_unpacked\*.scx')
    for fn in fl:
        export_text(fn)
        
if __name__ == "__main__":
    main()

