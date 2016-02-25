import struct,os,codecs
import shutil
import sys
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            ext = name.split('.')[-1]
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst

def get_file_info(info_name):
    fp = codecs.open(info_name , 'rb' , "utf-16")
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

def repack(pack_name):
    if os.path.exists("import\\%s"%pack_name):
        os.remove("import\\%s"%pack_name)
    print("copying...")
    shutil.copy ('bind\\%s'%pack_name, 'import\\%s'%pack_name)
    print("%s copyed..."%pack_name)
    fp = open("import\\%s"%pack_name , "rb+")
    patch_names = getpatch("import\\bind\\%s"%pack_name[:-4])
    index = get_file_info("bind_data\\bind\\%s.ini"%pack_name)
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
            patch_file = open("%s\\%s"%("import\\bind\\%s"%pack_name[:-4] , name) , "rb")
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

ABSPATH=os.path.abspath(sys.argv[0])
ABSPATH=os.path.dirname(ABSPATH)+"\\" + "import\\bind\\" 
fl = os.listdir("import\\bind")
for fn in fl:
    print(ABSPATH + fn)
    if os.path.isdir(ABSPATH + fn):
        repack(fn + ".bnd")

os.system("pause")
