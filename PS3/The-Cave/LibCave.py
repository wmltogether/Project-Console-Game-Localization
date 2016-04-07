# -*- coding: utf-8 -*-
import os,struct,codecs,zlib
from cStringIO import StringIO
import binascii
import zlib
def compress_zlib(string):
    compressed_string=zlib.compress(string,9)
    return compressed_string
def decompress_zlib(string):
    decompressed_string=zlib.decompress(string)
    return decompressed_string
def compress_deflate(string):
    compressed_string=zlib.compress(string)[2:-4]
    return compressed_string
def decompress_deflate(string):
    decompressed_string=zlib.decompress(string, -15)
    return decompressed_string
def ReadV5Bundle(f_buffer):
    #if version in 0x4h is 5: set file index is v5
    PAK_child_list=[]
    position=0
    sizeOfFileRecode = 0x10
    f_buffer.seek(8)
    FileExtensionOffset=struct.unpack('>Q',f_buffer.read(8))[0]
    NameDirOffset=struct.unpack('>Q',f_buffer.read(8))[0]
    FileExtensionCount=struct.unpack('>I',f_buffer.read(4))[0]
    NameDirSize=struct.unpack('>I',f_buffer.read(4))[0]
    numFiles=struct.unpack('>I',f_buffer.read(4))[0]
    f_buffer.seek(20,1)
    FileRecordsOffset=struct.unpack('>Q',f_buffer.read(8))[0]
    FooterOffset1=struct.unpack('>Q',f_buffer.read(8))[0]
    FooterOffset2=struct.unpack('>Q',f_buffer.read(8))[0]
    unk=struct.unpack('>I',f_buffer.read(4))[0]
    Marker2=struct.unpack('>I',f_buffer.read(4))[0]
    for i in range(0,numFiles):
        position=FileRecordsOffset+sizeOfFileRecode*i
        index_tmp_ofs=FileRecordsOffset+sizeOfFileRecode*i
        f_buffer.seek(position)
        # 48 bit UnCompressedSize
        #
        UnCompressedSize=struct.unpack('>I',f_buffer.read(4))[0]>>8
        f_buffer.seek(-1,1)
        NameOffset=struct.unpack('>I',f_buffer.read(4))[0]>>11
        f_buffer.seek(1,1)
        offset=struct.unpack('>I',f_buffer.read(4))[0]>>3
        f_buffer.seek(-1,1)
        t0=struct.unpack('>I',f_buffer.read(4))[0]
        #size=(t0>>5)>>9#PC Size
        #print(size)
        #if size==0:
        size=(t0>>4)#IOS size
        f_buffer.seek(-1,1)
        FileTypeIndex=(struct.unpack('>I',f_buffer.read(4))[0]>>4) >> 24
        FileTypeIndex=FileTypeIndex >> 1
        f_buffer.seek(-3,1)
        CompressionType=ord(f_buffer.read(1))&0x0f
        if CompressionType==4:
            Compressed=False
        elif CompressionType==8:
            Compressed=True
        else:
            print('Unknown compression type')
        #Get filename from filenames table
        position=NameDirOffset + NameOffset
        f_buffer.seek(position)
        FileName=f_buffer.read(255).split('\x00')[0]
        PAK_child_list.append((FileName,\
                               offset,\
                               size,\
                               UnCompressedSize,\
                               Compressed,\
                               index_tmp_ofs))
        '''
        print(FileName)
        print('Size when decompressed:%08x'%UnCompressedSize)
        print('Name offset %08x'%(NameDirOffset + NameOffset))
        print('Size %08x'%size)
        print('Offset %08x'%offset)
        print('Filetype index %x'%FileTypeIndex)
        print('Comp Type %x'%CompressionType)
        '''
    return PAK_child_list
