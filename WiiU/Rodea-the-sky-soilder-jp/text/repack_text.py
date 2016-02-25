import codecs,struct,os
from glob import iglob
from cStringIO import StringIO

def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst

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


def repack_text(filename):
    fp = open(filename[:-4].replace("__" , "\\") ,"rb")
    data = fp.read()
    sig = data[:4]
    fp.close()
    buffer = StringIO()
    buffer.write(data)
    buffer.seek(0)
    lines = codecs.open("CNtext\\%s"%filename , "rb" , 'utf-16').readlines()
    string_list, head_list = makestr_lines(lines)
    if sig == "TALD":
        buffer.seek(0X8)
        index0 = struct.unpack(">I" , buffer.read(4))[0]
        index1 = struct.unpack(">I" , buffer.read(4))[0]
        buffer.seek(0x20 + index0 * 0x10 + index1 * 0x20 )
        buffer.truncate()
        buffer.seek(0,2)
        for i in xrange(len(string_list)):
            string = string_list[i]
            string = string.replace("\r" ,"")
            string = string.replace("{end}" , u"\u0000")
            string = string.encode("utf-16be")
            ofs0 = buffer.tell()
            buffer.write(string)
            buffer.seek(0x20 + index0 * 0x10 + i * 0x20 + 0x14 )
            buffer.write(struct.pack(">I" , ofs0))
            buffer.seek(0,2)
    if sig == "TXTD":
        buffer.seek(0X8)
        index0 = struct.unpack(">I" , buffer.read(4))[0]
        buffer.seek(0x20 + index0 * 0x4)
        buffer.truncate()
        for i in xrange(len(string_list)):
            string = string_list[i]
            string = string.replace("\r" ,"")
            string = string.replace("{end}" , u"\u0000")
            string = string.encode("utf-16be")
            ofs0 = buffer.tell()
            buffer.write(string)
            buffer.seek(0x20 + i * 4)
            buffer.write(struct.pack(">I" , ofs0))
            buffer.seek(0,2)
    data = buffer.getvalue()
    folder = os.path.dirname("import\\%s"%filename[:-4].replace("__" , "\\"))
    if not os.path.exists(folder):
        os.makedirs(folder)
    dest = open("import\\%s"%filename[:-4].replace("__" , "\\") ,"wb")
    dest.write(data)
    if (len(data)%0x80 != 0):
        dest.write("\x00" * (0x80 - len(data)%0x80))
    dest.close()

fl = os.listdir("cntext")
for fn in fl:
    repack_text(fn)






