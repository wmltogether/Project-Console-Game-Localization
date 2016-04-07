import os,sys
import win32ui
import traceback
from LibCave import *
def export_cave(fn):
    f=open('%s.~p'%fn[:-3],'rb')
    header=open('%s.~h'%fn[:-3],'rb')
    F_size=os.path.getsize(fn)
    PAK_child_list=ReadV5Bundle(header)
    for i in range(len(PAK_child_list)):
        (FileName,offset,size,UnCompressedSize,\
         Compressed,index_tmp_ofs)=PAK_child_list[i]
        print('%s offset:%08x size:%08x UnCompressedSize:%08x Compressed:%d index_tmp_ofs:%08x'%(FileName,offset,size,UnCompressedSize,\
                                           Compressed,index_tmp_ofs))
        fldr='/'.join(FileName.split(r'/')[:-1])
        name=FileName.split(r'/')[-1]
        if not os.path.isdir('%s_unpacked\\%s\\'%(fn,fldr)):
            os.makedirs('%s_unpacked\\%s\\'%(fn,fldr))
        dest=open('%s_unpacked\\%s'%(fn,FileName),'wb')
        f.seek(offset)
        zdata=f.read(size)
        if Compressed==True:
            data=decompress_zlib(zdata)
        else:
            data=zdata
        dest.write(data)
        dest.close()
    f.close()
    header.close()
def main():
    dlg = win32ui.CreateFileDialog(1)
    dlg.SetOFNInitialDir('./')
    dlg.DoModal()
    filename = dlg.GetPathName()
    fn=filename
    try:
        export_cave(fn)
    except:
        traceback.print_exc()
    os.system('pause')
    os._exit(0)
if __name__=='__main__':
    main()

        
