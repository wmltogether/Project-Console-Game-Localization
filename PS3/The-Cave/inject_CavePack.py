# -*- coding: utf-8 -*-
import os,struct,codecs,zlib
from cStringIO import StringIO
import binascii
import zlib
from ctypes import *
from LibCave import *
from bitio import *
import win32ui
user32 = windll.LoadLibrary('user32.dll')
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def getLastPosition(PAK_child_list):
    last_num=len(PAK_child_list)
    (FileName,offset,size,UnCompressedSize,
     Compressed,index_tmp_ofs)=PAK_child_list[last_num-1]
    size+=((0x800-size%0x800)%0x800)
    last_offset=size+offset
    return last_offset
def inject_cave(fn):
    f=open('%s.~p'%fn[:-3],'rb+')
    header=open('%s.~h'%fn[:-3],'rb+')
    F_size=os.path.getsize('%s.~p'%fn[:-3])
    PAK_child_list=ReadV5Bundle(header)
    last_offset=getLastPosition(PAK_child_list)
    PAK_child_dict={}
    for i in range(len(PAK_child_list)):
        (FileName,offset,size,UnCompressedSize,\
         Compressed,index_tmp_ofs)=PAK_child_list[i]
        PAK_child_dict[FileName]=(index_tmp_ofs,offset,size,Compressed)
    if not os.path.isdir('files'):
        print(u'缺少files文件夹，请把要注入的文件夹放入files中')
        os.makedirs('files')
    file_list=dir_fn('files')
    i=0
    end_offset=last_offset
    print('Last Position is %08x'%end_offset)
    f.seek(end_offset)
    f.truncate()
    print('end_offset:%08x'%end_offset)
    for fs in file_list:
        nfs=fs[6:].replace('\\','/')
        if not nfs in PAK_child_dict:continue
        dest=open(fs,'rb')
        dat=dest.read()
        dest.close()
        UnCompressedSize=len(dat)
        (index_tmp_ofs,ori_offset,ori_size,Compressed)=PAK_child_dict[nfs]
        if Compressed==True:
            zdata=compress_zlib(dat)
        else:
            zdata=dat
        CompressedSize=len(zdata)
        print('%08x--->%08x'%(ori_size,CompressedSize))
        if CompressedSize<=ori_size+(0x800-ori_size%0x800)%0x800:
            print('%s:smaller than original file'%(nfs))
            f.seek(ori_offset)
            f.write(zdata)
            f.write('\x00'*((0x800-CompressedSize%0x800)%0x800))
            header.seek(index_tmp_ofs)
            b0=struct.pack('>I',UnCompressedSize<<8)[:3]
            header.write(b0)
            header.seek(index_tmp_ofs+4)
            header.seek(-1,1)
            header.seek(4,1)#NameOffset
            header.seek(1,1)
            b1=struct.pack('>I',ori_offset<<3)[:3]
            header.write(b1)
            print('CHECK1:%08x'%header.tell())#FF73
            t0=CompressedSize
            header.seek(header.tell())
            t1=header.read(4)
            print('CHECK2:%08x'%header.tell())#FF77
            print('%08x'%(struct.unpack('>I',t1)[0]))
            c_buff=StringIO()
            d_buff=StringIO()
            c_buff.write(t1)
            c_buff.seek(0)
            buf_in=BitIO(c_buff,ROPEN)
            buf_out=BitIO(d_buff,WOPEN)
            d0=buf_in.getbits(4)
            d1=buf_in.getbits(24)
            d2=buf_in.getbits(4)
            buf_out.putbits(4,d0)
            buf_out.putbits(24,t0)
            buf_out.putbits(4,d2)
            t1=d_buff.getvalue()
            header.seek(-4,1)
            header.write(t1)
        else:
            print('%s:bigger than original file goto:%08x'%(nfs,end_offset))
            f.seek(end_offset)
            ori_offset=f.tell()
            f.write(zdata)
            f.write('\x00'*((0x800-CompressedSize%0x800)%0x800))
            end_offset=f.tell()
            header.seek(index_tmp_ofs)
            b0=struct.pack('>I',UnCompressedSize<<8)[:3]
            header.write(b0)
            header.seek(index_tmp_ofs+4)
            header.seek(-1,1)
            header.seek(4,1)#NameOffset
            header.seek(1,1)
            b1=struct.pack('>I',ori_offset<<3)[:3]
            header.write(b1)
            print('CHECK1:%08x'%header.tell())#FF73
            t0=CompressedSize
            header.seek(header.tell())
            t1=header.read(4)
            print('CHECK2:%08x'%header.tell())#FF77
            print('%08x'%(struct.unpack('>I',t1)[0]))
            c_buff=StringIO()
            d_buff=StringIO()
            c_buff.write(t1)
            c_buff.seek(0)
            buf_in=BitIO(c_buff,ROPEN)
            buf_out=BitIO(d_buff,WOPEN)
            d0=buf_in.getbits(4)
            d1=buf_in.getbits(24)
            d2=buf_in.getbits(4)
            buf_out.putbits(4,d0)
            buf_out.putbits(24,t0)
            buf_out.putbits(4,d2)
            t1=d_buff.getvalue()
            header.seek(-4,1)
            header.write(t1)
        i+=1
    f.seek(0,2)
    tmp_ofs=f.tell()
    f.write('z'*((0x10000-tmp_ofs%0x10000)%0x10000))
    f.close()
    header.close()
def main():
    dlg = win32ui.CreateFileDialog(1)
    dlg.SetOFNInitialDir('./')
    dlg.DoModal()
    filename = dlg.GetPathName()
    fn=filename
    try:
        inject_cave(fn)
    except:
        traceback.print_exc()
    os.system('pause')
    os._exit(0)
if __name__=='__main__':
    main()

