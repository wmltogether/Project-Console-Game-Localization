#coding=utf-8
from cStringIO import StringIO
from PIL import Image
import os,glob,struct
import extmx
import exctf
from imptmx import tmx_image_encode
from osmod import dir_fn,mod_name
if not os.path.isdir('png\\'): os.makedirs('png\\')
if not os.path.isdir('tmx\\'): os.makedirs('tmx\\')
if not os.path.isdir('cnpng\\'): os.makedirs('cnpng\\')
if not os.path.isdir('cntmx\\'): os.makedirs('cntmx\\')
print(u'请将PNG图放入PNG文件夹内\r\n'+ \
      u'相应TMX,SPR,TMX图放入TMX文件夹内\r\n' +  \
      u'注意：所有PNG内像素值将按照原调色板写入TMX数据区\r\n'+ \
      u'本脚本依赖PIL(Python Imaging Library)\r\n'+\
      u'==================================\r\n'+\
      u'目前支援游戏：PSP/PS2 PERSONA3\r\n'+\
      u'　　　　　　　PS2 PERSONA4\r\n'+\
      u'　　　　　　　PSP/PS2 恐怖惊魂夜2\r\n'+\
      u'　　　　　　　PS3/X360 凯瑟琳\r\n')
fl=glob.iglob(r'png/*.png')
fd=dir_fn('tmx')
for fn in fl:
    (rname,tmx_id)=mod_name(fn[4:])
    print('tmx\\%s'%rname)
    if 'tmx\\%s'%rname in list(fd):
        print(u'>>>Load:%s'%fn[4:])
        bk = open('tmx\\%s'%rname,'rb+')
        data = bk.read()
        ddd = open('cntmx\\%s'%rname,'wb')
        ddd.write(data)
        ddd.close()
        bk.close()
        f=open('cntmx\\%s'%rname,'rb+')
        c_mark=0
        tmx_addr=0
        if rname[-4:].lower()=='.tmx':
            h_size=0x40
            f.seek(0)
        elif rname[-4:].lower()=='.ctf':
            c_mark=1
            h_size=0x60
            f.seek(0)
        elif rname[-4:].lower()=='.spr':
            f.seek(0xc)
            soffset=struct.unpack('I',f.read(0x4))[0]
            ind=int(tmx_id,10)
            f.seek(soffset+ind*8)
            null=struct.unpack('I',f.read(0x4))[0]
            tmx_addr=struct.unpack('I',f.read(0x4))[0]
            h_size=0x40
        else:
            h_size=0x40
            print(rname[-4:]+'Unknown File type,try tmx')
        f.seek(tmx_addr)
        head_dat=f.read(h_size)
        head_buff=StringIO()
        head_buff.write(head_dat)
        if c_mark==0:
            (filetype,tmx_size,width,height,bpp)=extmx.get_head_info(head_buff)#获取图片信息
        else:
            (filetype,width,height,bpp)=exctf.get_head_info(head_buff)#获取图片信息
            tmx_size=width*height*bpp/8+(0x40<<(bpp-4))
            tmx_addr=0x20
        f.seek(h_size+tmx_addr)   
        image_buff=StringIO()
        image_buff.write(f.read(tmx_size-h_size))
        im=Image.open(fn).convert('RGBA')
        print('TMX info:\r\n%s:|Width:%d|Height:%d|BPP:%d'%(filetype,width,height,bpp))
        print('PNG info:\r\n|Width:%d|Height:%d|RGBA'%(im.size[0],im.size[1]))        
        imdata=tmx_image_encode(width,height,bpp,image_buff,im)
        if bpp==4 and len(imdata)==width*height/2:
            f.seek(h_size+0x40+tmx_addr)
            f.write(imdata)
        elif bpp==8 and len(imdata)==width*height:
            f.seek(h_size+0x400+tmx_addr)
            f.write(imdata)
        elif bpp==32 and len(imdata)==width*height*4:
            f.seek(h_size+tmx_addr)
            f.write(imdata)    
        else:
            print('wrong bpp and image data')
        f.close()
        sss = open('cntmx\\%s'%rname,'rb')
        data = sss.read()
        sss.close()
        mPath =  os.path.basename('cntmx\\%s'%rname)
        mPath = mPath.replace("--", "\\")
        mPath = "..\\PATCH\\" + mPath
        print("write to" + mPath)
        pp = os.path.split(mPath)[0]
        if not (os.path.exists(pp)):
            os.makedirs(pp)
        qqq = open(mPath,'wb')
        qqq.write(data)
        qqq.close()
    else:
        print(u'>>>Load:%s Error no TMX image'%fn)
os.system('pause')
            
        
        
