# -*- coding: utf-8 -*-
import codecs,os,struct,zlib
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def compress_deflate(string):
    compressed_string=zlib.compress(string)[2:-4]
    return compressed_string
def decompress_deflate(string):
    decompressed_string=zlib.decompress(string, -15)
    return decompressed_string
def compress_zlib(string):
    compressed_string=zlib.compress(string)
    return compressed_string
def decompress_zlib(string):
    decompressed_string=zlib.decompress(string)
    return decompressed_string
def getIndexList(fn):
    fp = open(fn,'rb')
    fp.seek(0xc)
    BASE_OFF = struct.unpack('>I',fp.read(4))[0]
    nums = struct.unpack('>I',fp.read(4))[0]
    fp.seek(0x38)
    r_nums = struct.unpack('>I',fp.read(4))[0]
    index_list = []
    for i in range(nums):
        unk0 = struct.unpack('>I',fp.read(4))[0]
        tmp_ofs = fp.tell()
        size = struct.unpack('>I',fp.read(4))[0]
        compressed_size = struct.unpack('>I',fp.read(4))[0]
        TSTAMP = struct.unpack('>Q',fp.read(8))[0]
        offset = struct.unpack('>Q',fp.read(8))[0]
        if unk0 == 2:
            unk4,unk5 = struct.unpack('>2I',fp.read(8))
        folder_name_length = struct.unpack('>I',fp.read(4))[0]
        folder_name = fp.read(folder_name_length)
        name_length = struct.unpack('>I',fp.read(4))[0]
        name = fp.read(name_length)
        offset += BASE_OFF
        comFlag = False
        if compressed_size != 0:
            comFlag = True
        unk6,unk7 = struct.unpack('>2I',fp.read(8))
        index_list.append((comFlag,offset,size,compressed_size,folder_name,name,tmp_ofs))
    fp.close()
    return index_list
def unpack_ipk(fn):
    fp = open(fn,'rb')
    fp.seek(0xc)
    BASE_OFF = struct.unpack('>I',fp.read(4))[0]
    nums = struct.unpack('>I',fp.read(4))[0]
    fp.seek(0x38)
    r_nums = struct.unpack('>I',fp.read(4))[0]
    index_list = getIndexList(fn)
    for i in range(nums):
        (comFlag,offset,size,compressed_size,folder_name,name,tmp_ofs)=index_list[i]
        if not os.path.isdir('%s_unpacked\\%s'%(fn,folder_name)):
            os.makedirs('%s_unpacked\\%s'%(fn,folder_name))
        dest = open('%s_unpacked\\%s%s'%(fn,folder_name,name),'wb')
        fp.seek(offset)
        if comFlag == True:
            data = fp.read(compressed_size)
            data = decompress_zlib(data)
        else:
            data = fp.read(size)
        dest.write(data)
        dest.close()
    fp.close()
def inject_ipk(fn):
    fp = open(fn,'rb+')
    fp.seek(0xc)
    BASE_OFF = struct.unpack('>I',fp.read(4))[0]
    fsize = os.path.getsize(fn)
    index_list = getIndexList(fn)
    last_offset = fsize
    ipk_child_dict={}
    for i in range(len(index_list)):
        (comFlag,offset,size,\
         compressed_size,folder_name,name,tmp_ofs)=index_list[i]
        ipk_child_dict[folder_name+name] = (comFlag,offset,size,compressed_size,tmp_ofs)
    if not os.path.isdir('files'):
        print(u'缺少files文件夹,请把要注入的文件夹放入files中')
        os.makedirs('files')
    file_list=dir_fn('files')
    i = 0
    end_offset = last_offset
    fp.seek(end_offset)
    fp.truncate()
    for fs in file_list:
        nfs = fs[6:].replace('\\','/')
        if not nfs in ipk_child_dict:continue
        print('%s:inject'%nfs)
        dest = open(fs,'rb')
        data = dest.read()
        dest.close()
        file_size = len(data)
        file_compressed_size = 0
        (comFlag,ori_offset,ori_size,ori_compressed_size,tmp_ofs) = ipk_child_dict[nfs]
        if comFlag == True:
            data = compress_zlib(data)
            file_compressed_size = len(data)
            if file_compressed_size <= ori_compressed_size:
                fp.seek(ori_offset)
                fp.write(data)
                fp.seek(tmp_ofs)
                fp.write(struct.pack('>I',file_size))
                fp.write(struct.pack('>I',file_compressed_size))
            else:
                fp.seek(0,2)
                offset = fp.tell()
                offset -= BASE_OFF
                fp.write(data)
                fp.seek(tmp_ofs)
                fp.write(struct.pack('>I',file_size))
                fp.write(struct.pack('>I',file_compressed_size))
                p0 = fp.tell()
                fp.seek(p0)
                fp.seek(8,1)
                fp.write(struct.pack('>Q',offset))
        else:
            if file_size <= ori_size:
                fp.seek(ori_offset)
                fp.write(data)
                fp.seek(tmp_ofs)
                fp.write(struct.pack('>I',file_size))
                fp.write(struct.pack('>I',file_compressed_size))
            else:
                fp.seek(0,2)
                offset = fp.tell()
                offset -= BASE_OFF
                fp.write(data)
                fp.seek(tmp_ofs)
                fp.write(struct.pack('>I',file_size))
                fp.write(struct.pack('>I',file_compressed_size))
                p0 = fp.tell()
                fp.seek(p0)
                fp.seek(8,1)
                fp.write(struct.pack('>Q',offset))
    fp.close()
        

   
    
