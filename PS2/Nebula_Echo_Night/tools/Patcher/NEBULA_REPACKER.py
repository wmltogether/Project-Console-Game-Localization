import struct,os,codecs
import shutil
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            ext = name.split('.')[-1]
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def get_file_info():
    fp = codecs.open('kuon.ini' , 'rb' , "utf-16")
    lines = fp.readlines()
    l = {}
    for i in xrange(len(lines)):
        line = lines[i]
        if '\t' in line:
            (file_id , offset, size ,name) = line.split('\t')[:4]
            file_id = i
            offset = int(offset, 16)
            size = int(size , 16)
            name = name.replace("\r\n" , "")
            l[name] = (file_id , offset, size)
    return l
    
def getpatch(folder):
    fl = dir_fn(folder)
    lst = []
    for fn in fl:
        lst.append(fn[len(folder):])
    return lst

def repack():
    if os.path.exists("import\\EN3.BND"):
        os.remove("import\\EN3.BND")
    print("copying...")
    shutil.copy ('EN3.BND', 'import\\EN3.BND')
    print("EN3.BND copyed...")
    fp = open("import\\EN3.BND" , "rb+")
    patch_names = getpatch("patch")
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
            fp.seek(0x20 + file_id * 0x10 + 4)
            offset, size = struct.unpack("2I" , fp.read(8))
            patch_file = open("patch\\%s"%name , "rb")
            patch_data = patch_file.read()
            if len(patch_data) <= size:
                size = len(patch_data)
                offset = offset
                print("Patch:%s >>> %08x,%d"%(name , offset, size))
                slen = 0
                
            else:
                fp.seek(0,2)
                size = len(patch_data)
                slen = 0
                if size%0x800 != 0:
                    slen = 0x800 - size%0x800
                offset = fp.tell()
                print("Inject:%s >>> %08x,%d"%(name , offset, size))
            fp.seek(offset)
            fp.write(patch_data)
            fp.write("\x00" * slen)
            fp.seek(0x20 + file_id * 0x10 + 4)
            fp.write(struct.pack("2I" , offset ,size))
            patch_file.close()
    fp.seek(0,2)
    end = fp.tell()
    fp.seek(0xc)
    fp.write(struct.pack("I" , end))
    fp.close()

repack()
os.system("pause")
