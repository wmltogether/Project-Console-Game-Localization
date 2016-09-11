# -*- coding:utf-8 -*-
import codecs
import struct
import glob
import os
from cStringIO import StringIO as BufferIO

def getTable(table_name):
    fp = codecs.open(table_name , 'rb' , 'utf-16')
    lines = fp.readlines()
    table_dict = {}
    for line in lines:
        if "=" in line:
            line = line.replace("\r" , "")
            line = line.replace("\n" , "")
            code = (line.split("=")[0]).upper()
            char = '='.join(line.split("=")[1:])
            table_dict[char] = code
    fp.close()
    return table_dict
    
def makestr_lines(lines):
    string_list = []
    head_list = []
    num = len(lines)
    for index, line in enumerate(lines):
        if u'####' in line:
            head_list.append(line[5:-7])
            i = 1
            string = ''
            while True:
                if index+i >= num:
                    break
                if '####' in lines[index+i]:
                    break
                string += lines[index+i]
                i += 1
            string_list.append(string[:-4])
    return string_list, head_list

def force_except_kanji(string):
    ns = u""
    for char in ns:
    	bd = char.encode("utf-16")[2:]
    	charcode = struct.unpack("I" , bd)[0]
    	if 0x30 <= charcode <= 0x7a:
    	    ns += char
    	else:
    	    pass

    return ns
def convert_string2code(string):

    import binascii
    if (("{" in string) and ("}" not in string)) or (("}" in string) and ("{" not in string)):
        print(u"error:{hex} in not in string:%s"%string)
        string = string.replace("}" , "")
        string = string.replace("{" , "")
    jis_table_dict = getTable("0char.txt")
    kanji_table_dict = getTable(u"kanji_table.TBL")
    string_len = len(string)
    string_code = u""
    pos = 0
    while pos < string_len:
        char = string[pos]

        if char == u"{":
            pos += 1
            ctr_code = u""
            while True:
                ctr_char = string[pos]
                pos += 1
                if ctr_char == u"}":
                    break
                else:
                    ctr_code += ctr_char
            string_code += ctr_code
        elif char == u"}":
            pos += 1

        elif char in jis_table_dict:
            pos += 1
            char_code = jis_table_dict[char]
            string_code += char_code
        elif char in kanji_table_dict:
            pos += 1
            char_code = kanji_table_dict[char]
            string_code += char_code
        elif char == '\r':
            pos += 1
        elif char == '\n':
            pos += 1
        else:
            print('error:%s in not in kanji table'%char)
            break
    try:
    	string_code = binascii.a2b_hex(str(string_code.lower()))
    except:
    	print(u"error 控制符错误:%s"%string)
    	string_code = force_except_kanji(string_code)
    	string_code = binascii.a2b_hex(str(string_code.lower()))
    return string_code


def import_chaos(r_filename):
    if not os.path.exists("cn-text"):os.makedirs("cn-text")
    if not os.path.exists("import"):os.makedirs("import")
    text_file = codecs.open("cn-text/%s"%r_filename, "rb", "utf-16")
    text_lines = text_file.readlines()
    string_list, head_list = makestr_lines(text_lines)
    nums = len(string_list)
    code_list = []
    for i in xrange(nums):
        string = string_list[i]
        ptr_pos = int(head_list[i], 16) - 4
        # 因为导出的时候手滑写错了，所以手动 -4
        string_code = convert_string2code(string)
        code_list.append((ptr_pos, string_code))
    text_file.close()
    fileBuffer = BufferIO()
    ofile = open("script.cpk_unpacked/%s"%r_filename[:-4] , "rb")
    ofile_size = os.path.getsize("script.cpk_unpacked/%s"%r_filename[:-4])
    fileBuffer.write(ofile.read())
    ofile.close()
    fileBuffer.seek(0)
    fileBuffer.seek(4, 1)
    index_start_pos, = struct.unpack('I' , fileBuffer.read(4))
    fileBuffer.seek(index_start_pos)
    string_start_pos, = struct.unpack('I' , fileBuffer.read(4))
    fileBuffer.seek(string_start_pos)
    fileBuffer.truncate()
    str_pos = fileBuffer.tell()
    tmp = str_pos
    for (ptr_pos, string_code) in code_list:
        fileBuffer.seek(str_pos)
        fileBuffer.write(string_code)

        fileBuffer.write('\xFF')
        str_pos = fileBuffer.tell()
        fileBuffer.seek(ptr_pos)
        fileBuffer.write(struct.pack("I", tmp))
        tmp = str_pos
    fileBuffer.seek(0 ,2)
    end_pos = fileBuffer.tell()
    if end_pos <= ofile_size:
        fileBuffer.seek(end_pos)
        fileBuffer.write("\x00" * (ofile_size - end_pos))
    with open("import/%s"%r_filename[:-4] , "wb") as dest:
        print("write to >>>import/%s"%r_filename[:-4])
        dest.write(fileBuffer.getvalue())
        dest.close()
def main():
    fl = glob.iglob("cn-text\*.txt")
    for fn in fl:
        print(fn)
        fn = fn.split('\\')[-1]
        import_chaos(fn)
if __name__ == "__main__":
    print(u"Chaos;Child importer 0.9")
    print(u"only for wrong textfiles from old exporter")
    print(u"Please put chinese words into kanji_table.tbl, \n the beginning code is 8297")
    main()
    os.system("pause")
