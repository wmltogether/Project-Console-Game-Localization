#coding=utf-8
from cStringIO import StringIO
from PIL import Image
import os,struct
import extmx
import exctf
from osmod import dir_fn
if not os.path.isdir('tmx\\'): os.makedirs('tmx\\')
print(u'请将CTF,TMX和SPR图放入TMX文件夹内\r\n'+ \
      u'相应PNG会输出在PNG目录\r\n'+ \
      u'注意：输出格式为RGBA PNG\r\n'+ \
      u'本脚本依赖PIL(Python Imaging Library)\r\n'+\
      u'==================================\r\n'+\
      u'目前支援游戏：PSP/PS2 PERSONA3\r\n'+\
      u'　　　　　　　PS2 PERSONA4\r\n'+\
      u'　　　　　　　PSP/PS2 恐怖惊魂夜2\r\n'+\
      u'　　　　　　　PS3/X360 凯瑟琳\r\n')
fl=dir_fn('tmx')
if not os.path.isdir('png\\'): os.makedirs('png\\')
for fn in fl:
    if fn[-4:].lower()=='.tmx':
        print('Load:%s'%fn)
        f=open(fn,'rb')
        head_dat=f.read(0x40)
        head_buff=StringIO()
        head_buff.write(head_dat)
        (filetype,tmx_size,width,height,bpp)=extmx.get_head_info(head_buff)#获取图片信息
        if filetype=='TMX0':
            print('%s:|Width:%d|Height:%d|BPP:%d'%(filetype,width,height,bpp))
            f.seek(0x40)
            image_buff=StringIO()
            image_buff.write(f.read(tmx_size-0x40))
            pixtuple=extmx.tmx_image_decode(width,height,bpp,image_buff)#获取图片所有像素颜色值
            im = Image.new('RGBA',(width,height))
            im.putdata(pixtuple)#绘图
            im.save('png//%s.%dBPP.png'%(fn.split('\\')[1],bpp))
    elif fn[-4:].lower()=='.spr':
        print('Load:%s'%fn)
        f=open(fn,'rb')
        f.seek(0xc)
        soffset=struct.unpack('I',f.read(0x4))[0]
        ssize=struct.unpack('I',f.read(0x4))[0]
        tmx_num=struct.unpack('H',f.read(2))[0]
        f.seek(soffset)
        a=f.tell()
        for i in range(tmx_num):
            f.seek(a)
            null=struct.unpack('I',f.read(0x4))[0]
            tmx_addr=struct.unpack('I',f.read(0x4))[0]
            a=f.tell()
            f.seek(tmx_addr)
            head_dat=f.read(0x40)
            head_buff=StringIO()
            head_buff.write(head_dat)
            (filetype,tmx_size,width,height,bpp)=extmx.get_head_info(head_buff)#获取图片信息
            if filetype=='TMX0':
                print('%s:|Width:%d|Height:%d|BPP:%d'%(filetype,width,height,bpp))
                f.seek(0x40+tmx_addr)
                image_buff=StringIO()
                image_buff.write(f.read(tmx_size-0x40))
                pixtuple=extmx.tmx_image_decode(width,height,bpp,image_buff)#获取图片所有像素颜色值
                im = Image.new('RGBA',(width,height))
                im.putdata(pixtuple)#绘图
                im.save('png//%s.%04d.%dBPP.png'%(fn.split('\\')[1],i,bpp))
            else:
                print('Unknown filetype')
    elif fn[-4:].lower()=='.ctf':
        print('Load:%s'%fn)
        f=open(fn,'rb')
        head_buff=StringIO()
        head_dat=f.read(0x60)
        head_buff.write(head_dat)
        (filetype,width,height,bpp)=exctf.get_head_info(head_buff)
        print('%s:|Width:%d|Height:%d|BPP:%d'%(filetype,width,height,bpp))
        f.seek(0)
        image_buff=StringIO()
        image_buff.write(f.read())
        pixtuple=exctf.ctf_image_decode(width,height,bpp,image_buff)
        im = Image.new('RGBA',(width,height))
        im.putdata(pixtuple)#绘图
        im.save('png//%s.%dBPP.png'%(fn.split('\\')[1],bpp))
    else:
        print('Load:%s'%fn+r'Not TMX/CTF image')
    f.close()
os.system('pause')

