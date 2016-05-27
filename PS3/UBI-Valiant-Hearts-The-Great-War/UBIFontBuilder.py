#coding=cp936

import struct,os,codecs
#如果是相对坐标，需要设定基础坐标 base xy
BASE_X = 0
BASE_Y = 0
def getBMFInfo(line):
    d=line.split(' ')
    for s in d:
        if 'lineHeight=' in s:
            lineHeight=int(s[11:])
        if 'base=' in s:
            base=int(s[5:])
        if 'scaleW=' in s:
            scaleW=int(s[7:])
        if 'scaleH=' in s:
            scaleH=int(s[7:])
    if 'common' in d:
        return (lineHeight,base,scaleW,scaleH)
    else:
        return (0,0,0,0)
def split_key_value(v0):
    v1=v0.split('=')
    key=v1[0]
    value=v1[1].replace('\r\n','')
    return (key,value)
def getCharInfo_N(line):
    charBinary=''
    if ' ' and "char id" in line:
        linelist = line.split(' ')
        c_list=[]
        for i in  xrange(len(linelist)):
            value=linelist[i]
            if not value=='':
               c_list.append(value)
        #print(c_list)
        (charName,char_id)=split_key_value(c_list[1])
        (xName,x)=split_key_value(c_list[2])
        (yName,y)=split_key_value(c_list[3])
        (wName,width)=split_key_value(c_list[4])
        (hName,height)=split_key_value(c_list[5])
        (xoffName,xoffset)=split_key_value(c_list[6])
        (yoffName,yoffset)=split_key_value(c_list[7])
        (xadvName,xadvance)=split_key_value(c_list[8])
        (pageName,page)=split_key_value(c_list[9])
        (chnlName,chnl)=split_key_value(c_list[10])
        b0=(char_id,x,y,width,height,xoffset,yoffset,xadvance,page,chnl)
        (char_id,x,y,width,height,xoffset,yoffset,xadvance,page,chnl)=(int(char_id),int(x),int(y),int(width),int(height),\
                                                             int(xoffset),int(yoffset),int(xadvance),int(page),int(chnl))
        try:
            charBinary+=(struct.pack('>I',0x28)+\
                         struct.pack('>I',char_id)+\
                         struct.pack('>I',x)+\
                         struct.pack('>I',y)+\
                         struct.pack('>I',width)+\
                         struct.pack('>I',height)+\
                         struct.pack('>I',xoffset%0xffffffff)+\
                         struct.pack('>I',yoffset%0xffffffff)+\
                         struct.pack('>I',xadvance%0xffffffff)+\
                         struct.pack('>I',page)+\
                         struct.pack('>I',chnl))

        except:
            print('error!format:%s,%s,%s,%s,%s,%s,%s,%s,%s,%s'%b0)
    else:
        print('error bmfont file:%x'%len(line))
        
    return charBinary
def main():
    fn='font02.fnt'
    f=codecs.open(fn,'rb','gbk')
    lines=f.readlines()
    (lineHeight,base,scaleW,scaleH)=getBMFInfo(lines[1])
    num=int(lines[3][12:])
    print('Char NUM:%d'%num)
    bindat=''
    bindat+=(struct.pack('>I',num))
    for i in xrange(num):
        charline=lines[4+i].replace('\r\n','')
        charBinary=getCharInfo_N(charline)
        bindat+=charBinary
    dest=open('%s.tfn.ckd'%fn[:-4],'wb')
    dest.write('\x00\x00\x00\x01')
    dest.write('\x00\x00\x31\x14')
    dest.write('\x43\x3a\x0c\x96')
    dest.write('\x00\x00\x01\x2c')
    dest.write('\x00\x00\x00\x58')
    dest.write('\x00\x00\x00\x0f')
    dest.write('WorldWarOne_3.0')#设定字库名
    dest.write('\x00\x00\x00\x36')
    dest.write('\x00\x00\x00\x00'+'\x00\x00\x00\x00'+'\x00\x00\x00\x00'+'\x00\x00\x00\x01')
    dest.write('\x00\x00\x00\x64'+'\x00\x00\x00\x01'+'\x00\x00\x00\x01'+'\x00\x00\x00\x01')
    dest.write('\x00\x00\x00\x01'+'\x00\x00\x00\x01'+'\x00\x00\x00\x01'+'\x00\x00\x00\x04')
    dest.write('\x00\x00\x00\x04')
    dest.write('\x00\x00\x00\x00'+'\x00\x00\x00\x28'+'\x00\x00\x00\x36'+'\x00\x00\x00\x2e')
    dest.write(struct.pack('>I',2048))
    dest.write(struct.pack('>I',2048))
    dest.write('\x00\x00\x00\x01'+'\x00\x00\x00\x00'+'\x00\x00\x00\x00'+'\x00\x00\x00\x04')
    dest.write('\x00\x00\x00\x04'+'\x00\x00\x00\x04'+'\x00\x00\x00\x01'+'\x00\x00\x00\x58')
    dest.write('\x00\x00\x00\x00')
    dest.write('\x00\x00\x00\x16')
    dest.write(r'enginedata/misc/fonts/')
    dest.write('\x00\x00\x00\x0c')
    dest.write('font02_0.tga')
    dest.write('\x51\x28\x03\x49')
    dest.write('\x00\x00\x00\x00')
    dest.write(bindat)
    dest.close()
    f.close()
if __name__=='__main__':
    main()
    print('convert done')



