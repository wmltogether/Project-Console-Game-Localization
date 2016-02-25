# -*- coding: utf-8 -*-
import codecs,struct,os,binascii
from glob import iglob
from cStringIO import StringIO
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst

def maketbl():
    fp = codecs.open("base.TBL",'rb','utf-16')
    lines = fp.readlines()
    tbl_dict = {}
    for line in lines:
        if "=" in line:
            code,char = line.split("=")[:2]
            char = char.replace("\r\n" , "")
            code = code.lower()

            tbl_dict[char] = code
    fp = codecs.open("cn.TBL",'rb','utf-16')
    lines = fp.readlines()
    for line in lines:
        if "=" in line:
            code,char = line.split("=")[:2]
            char = char.replace("\r\n" , "")
            code = code.lower()
            tbl_dict[char] = code
    return tbl_dict

def makestr_lines(lines):
    string_list = []
    head_list = []
    num = len(lines)
    for index,line in enumerate(lines):
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

def findctr_code(string , original_text):
    if not "}" in string:
        print(u"error :[%s] >> } code is missing \n text: [%s]"%(string , original_text))
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

def string2hex(string):
    tbl_dict = maketbl()
    hex = ""
    pos = 0
    tmp_ctr = ""
    while pos < len(string):
        char = string[pos]
        if char == "{":
            ctr_str = findctr_code(string[pos:],string)
            if ctr_str.lower() == "LF":
                hex += "0a"
            elif ctr_str.lower() == "end":
                hex += "00"
            else:
                print(u"error :[%s] >> code is unrecognized\n text:[%s]"%(ctr_str,string))
            pos += len(ctr_str) + 2
        elif char in tbl_dict:
            char_code = tbl_dict[char]
            hex += char_code
            pos += 1
        elif char == "\n":
            hex += "0a"
            pos += 1
        elif char == "\r":
            pos += 1
        else:
            print(u"error :[%s]  char is not defined in tbl_dict\n text:[%s]"%(char,string))
            pos += 1
    return binascii.a2b_hex(hex.lower())


def rebuild_text(fn):
    textfile = codecs.open("cn-text\\%s"%fn , "rb" , "utf-16")
    textlines = textfile.readlines()
    string_list, head_list = makestr_lines(textlines)
    fp = open("jpdata\\%s"%fn[:-4] , "rb")
    data = fp.read()
    binaryWriter = StringIO()
    binaryWriter.seek(0)
    binaryWriter.write(data)
    binaryWriter.seek(0)
    fp.close()
    binaryWriter.seek(0x10)
    nums, = struct.unpack("I" , binaryWriter.read(4))
    boffset, = struct.unpack("I" , binaryWriter.read(4))
    binaryWriter.seek(boffset + 0x4 * nums)
    binaryWriter.truncate()
    tmp_offset = binaryWriter.tell()
    for i in xrange(len(string_list)):
        binaryWriter.seek(tmp_offset)
        string = string_list[i]
        string = string.replace("{232A}",r"#*")
        head = head_list[i]
        nid = int(head.split(",")[1])
        if not "{end}" in string:
            print(u"error :[%s] >> {end} is not in string"%string)
            string += "{end}"
        bindata = string2hex(string)
        text_offset = binaryWriter.tell()
        binaryWriter.write(bindata)
        tmp_offset = binaryWriter.tell()
        binaryWriter.seek(boffset + 0x4 * nid)
        binaryWriter.write(struct.pack("I" , text_offset))
    binaryWriter.seek(0,2)
    total_size = binaryWriter.tell()
    binaryWriter.seek(4)
    binaryWriter.write(struct.pack("I" , total_size))
    binaryWriter.seek(0)
    data = binaryWriter.getvalue()
    folder  = fn[:-4].replace("__" , "\\")
    folder = "\\".join(folder.split("\\")[:-1])
    if not os.path.exists("import\\%s"%folder):
        os.makedirs("import\\%s"%folder)
    dest = open("import\\%s"%fn[:-4].replace("__" , "\\") , "wb")
    dest.write(data)
    dest.close()


def main():
    fl = os.listdir("cn-text")
    for fn in fl:
        if ".txt" in fn[-4:].lower():
            print(fn)
            rebuild_text(fn)

if __name__ == '__main__':
    main()






