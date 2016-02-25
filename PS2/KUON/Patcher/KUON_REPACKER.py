import struct,os,codecs
import shutil
def get_file_info():
    fp = open('kuon.ini' , 'rb')
    lines = fp.readlines()
    l = {}
    for line in lines:
        if '\t' in line:
            (file_id , offset, size ,name) = line.split('\t')[:4]
            file_id = int(file_id , 10)
            offset = int(offset, 16)
            size = int(size , 16)
            name = name.replace("\r\n" , "")
            l[name] = (file_id , offset, size)
    return l
def repack():
    if os.path.exists("import\\all.bnd"):
        os.remove("import\\all.bnd")
    shutil.copy ('all.bnd', 'import\\all.bnd')
    fp = open("import\\all.bnd" , "rb+")
    patch_names = os.listdir("patch")
    index = get_file_info()
    fp.seek(0,2)
    end = fp.tell()
    slen = 0
    if end%0x800 != 0:
        slen = 0x800 - end%0x800
    fp.write("\x00" * slen)
    fp.seek(0)
    for name in patch_names:
        if name in index:
            (file_id , offset, size) = index[name]
            fp.seek(0x10 + file_id * 0x10 + 4)
            offset, size = struct.unpack("2I" , fp.read(8))
            patch_file = open("patch\\%s"%name , "rb")
            patch_data = patch_file.read()
            if len(patch_data) <= size:
                size = len(patch_data)
                offset = offset
                slen = 0
            else:
                fp.seek(0,2)
                size = len(patch_data)
                slen = 0
                if size%0x800 != 0:
                    slen = 0x800 - size%0x800
                offset = fp.tell()
            print("Patch:%s >>> %08x,%d"%(name , offset, size))
            fp.seek(offset)
            fp.write(patch_data)
            fp.write("\x00" * slen)
            fp.seek(0x10 + file_id * 0x10 + 4)
            fp.write(struct.pack("2I" , offset ,size))
            patch_file.close()
    fp.seek(0,2)
    end = fp.tell()
    fp.seek(0x8)
    fp.write(struct.pack("I" , end))
    fp.close()

repack()
os.system("pause")
