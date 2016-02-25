 # -*- coding: utf-8 -*-
import wx
import wx._gdi
import codecs
from StringIO import StringIO
import struct
import os
from PIL import Image,ImageColor
from GIDecode import *

def csv2data(csv_name):
    data_list = []
    fp = open(csv_name , "rb")
    lines = fp.readlines()
    for line in lines:
        if "," in line:
            line = line.replace("\r\n" , "")
            char_code , x, y ,char_width , char_height , pid = line.split(",")[:6]
            char_code = int(char_code)
            x = int(x)
            y = int(y)
            char_width = int(char_width)
            char_height = int(char_height)
            data_list.append((char_code ,x,y,char_width,char_height))
    fp.close()
    return data_list
class Fonttool:
    def __init__(self):
        self.font_height = 0x12
        self.image_width = 1024
        self.image_height = 1024
        self.block0_nums = 0
        self.block1_nums = 0

    def _makeCodeBin(self , ccm_lst):
        binaryWriter = StringIO()
        binaryWriter.seek(0)
        tmp = 0
        for i in xrange(len(ccm_lst)):
            items = ccm_lst[i]
            (code_begin , code_end) = items
            
            binaryWriter.write(struct.pack("3I" , code_begin , code_end , tmp))
            tmp += (code_end - code_begin + 1)
        data = binaryWriter.getvalue()
        return data

    def _makeXYbin(self , current_image_width , current_image_height , current_csv):
        data_list = csv2data(current_csv)
        image_nums = 1
        charnums = len(data_list)
        binaryWriter = StringIO()
        binaryWriter.seek(0)
        x0 = 0
        y0 = 0
        d = 0 # d是图片序号
        for v in xrange(len(data_list)):
            code,x0,y0,cw,ch = data_list[v]
            x0 = x0
            y0 = y0
            x1 = x0 + cw
            y1 = y0 + ch
            a = 1
            b = cw - 1
            c = cw
            binaryWriter.write(struct.pack("ffffHHHH" , x0/float(current_image_width),
                                                        y0/float(current_image_height),
                                                        x1/float(current_image_width),
                                                        y1/float(current_image_height),
                                           a,b,c,d))

        data = binaryWriter.getvalue()
        return data

    def build_ccm(self , ccm_name , current_image_width , current_image_height , current_csv , dest_name):
        self.block0_nums = 0
        self.block1_nums = 0
        current_height = csv2data(current_csv)[0][-1]
        ccm_file = open(ccm_name , "rb")
        ccm_lines = ccm_file.readlines()
        char_nums = int(ccm_lines[0].split(":")[1].split("]")[0])
        ccm_lst = []
        for i in xrange(1,len(ccm_lines)):
            line = ccm_lines[i]
            if "," in line:
                (code_begin , code_end) = line.split(",")[:2]
                code_begin = int(code_begin, 16)
                code_end = int(code_end, 16)
                self.block1_nums += (code_end - code_begin + 1)
                ccm_lst.append((code_begin , code_end))
        self.block0_nums = len(ccm_lst)
        print("%d"%self.block0_nums)
        fontBuffer = StringIO()
        fontBuffer.seek(0)
        fontBuffer.write(struct.pack("I" , 0x010000))
        fontBuffer.write(struct.pack("I" , 0))#文件总长度
        fontBuffer.write(struct.pack("I" , current_height))
        fontBuffer.write(struct.pack("I" , 0))
        fontBuffer.write(struct.pack("H" , self.block0_nums))
        fontBuffer.write(struct.pack("H" , self.block1_nums))
        fontBuffer.write(struct.pack("I" , 0x20)) #写入block起始地址
        fontBuffer.write(struct.pack("I" , 0x20 + self.block0_nums * 0xc))#写入block1起始地址
        fontBuffer.write(struct.pack("I" , 0x010000))
        fontBuffer.write("\x00" * (self.block0_nums * 0xc))
        fontBuffer.write("\x00" * (self.block1_nums * 0x18))
        fontBuffer.seek(0,2)
        end_offset = fontBuffer.tell()
        fontBuffer.seek(4)
        fontBuffer.write(struct.pack("I" ,end_offset))
        fontBuffer.seek(0x20)
        data = self._makeCodeBin(ccm_lst)
        fontBuffer.write(data)
        fontBuffer.seek(0x20 + self.block0_nums * 0xc)
        data = self._makeXYbin(current_image_width , current_image_height , current_csv)
        fontBuffer.write(data)
        fontBuffer.seek(0)
        destdata = fontBuffer.getvalue()
        dest = open("build//%s"%dest_name , "wb")
        dest.write(destdata)
        end = dest.tell()
        if end%0x10 > 0:
            dest.write("\x00" * (0x10 - end%0x10))
        dest.close()

        return True

    def export_charlist(self , fn):
        dest = codecs.open("charlist.txt" ,"wb" ,"utf-16")
        fp = open(fn ,"rb")
        fp.seek(0x4)
        fsize = struct.unpack("I" , fp.read(4))[0]
        fp.seek(0x8)
        font_height = struct.unpack("I" , fp.read(4))[0] #字体高度
        image_nums = 512 / font_height # 字库张数
        fp.seek(0x10)
        block0_nums = struct.unpack("H" , fp.read(2))[0]
        block1_nums = struct.unpack("H" , fp.read(2))[0]
        block0_offset = struct.unpack("I" , fp.read(4))[0]
        block1_offset = struct.unpack("I" , fp.read(4))[0]
        fp.seek(4,1)
        fp.seek(block0_offset)
        code_list = []
        for i in xrange(block0_nums):
            fp.seek(block0_offset + 0xc * i)
            tmp = hex(fp.tell())
            code0 , code1 , nid = struct.unpack("3I" , fp.read(0xc))
            for j in xrange(code0 , code1):
            	codeA = j
                if codeA < 0x100:
                    ucode0 = struct.pack("B" , codeA).decode("cp932")
                else:
                    ucode0 = struct.pack(">H" , codeA).decode("cp932")

                if not ucode0 in code_list:
                    code_list.append(ucode0)
        dest.write("".join(code_list))
        dest.close()
        fp.close()

        return None
    def export_font_info(self , fn):
        m_width = 1024
        m_height = 512
        dest = codecs.open("font_info.csv" ,"wb" ,"utf-8")
        fp = open(fn ,"rb")
        fp.seek(0x4)
        fsize = struct.unpack("I" , fp.read(4))[0]
        fp.seek(0x10)
        block0_nums = struct.unpack("H" , fp.read(2))[0]
        block1_nums = struct.unpack("H" , fp.read(2))[0]
        block0_offset = struct.unpack("I" , fp.read(4))[0]
        block1_offset = struct.unpack("I" , fp.read(4))[0]
        fp.seek(4,1)
        fp.seek(block0_offset)
        code_dict = {}
        for i in xrange(block0_nums):
            fp.seek(block0_offset + 0xc * i)
            tmp = hex(fp.tell())
            code0 , code1 , nid = struct.unpack("3I" , fp.read(0xc))
            if code0 < 0x100:
                ucode0 = struct.pack("B" , code0).decode("cp932") #JIS起始编码
            else:
                ucode0 = struct.pack(">H" , code0).decode("cp932") #JIS起始编码

            if code1 < 0x100:
                ucode1 = struct.pack("B" , code1).decode("cp932") #JIS结束编码
            else:
                ucode1 = struct.pack(">H" , code1).decode("cp932") # JIS结束编码
            code_dict[nid] = (code0 , code1,ucode0, ucode1)
        fp.seek(block1_offset)
        for i in xrange(block1_nums):
            fp.seek(block1_offset + 0x18 * i)
            (x0 , y0 ,x1, y1 , a,b,c,d) = struct.unpack("ffffHHHH" , fp.read(0x18))
            x0 = x0 * float(m_width)
            y0 = y0 * float(m_height)
            x1 = x1 * float(m_width)
            y1 = y1 * float(m_height)
            dest.write("%f,%f,%f,%f,%d,%d,%d,%d,"%(x0,y0,x1,y1,a,b,c,d))
            if i in code_dict:
                code0 , code1,ucode0, ucode1 = code_dict[i]
                dest.write("%s,%x,%s,%x,"%(ucode0,code0,ucode1,code1))
            else:
                dest.write(",,,,")
            dest.write("\r\n")
        dest.close()
        fp.close()

        return None

    def expng(self , fn):
        if not os.path.exists("png"):
            os.makedirs("png")
        fp = open("%s"%fn , "rb")
        fp.seek(5)
        s = struct.unpack("H" , fp.read(2))[0]/0x400
        m_width = 1024
        m_height = 512 * s
        fp.seek(0x20)
        image_data = fp.read(m_height * m_width / 2)
        palette_data = fp.read(0x40)
        palette_list = getPaletteData(palette_data , \
                                              0x80 , 4 , False , 0 )
        pixel_list = paint_4BPP(m_width, m_height, m_width, m_height,
                                       image_data,
                                       palette_list,
                                       'BIG',
                                       'PS2')
        im = Image.new('RGBA', (m_width, m_height))
        im.putdata(tuple(pixel_list))
        im.save('png\\%s.png'%(fn))
        fp.close()


class wxFont(wx.Frame):
    def OnClick_excharlist(self ,event):
        fonttool = Fonttool()
        fonttool.export_charlist("Font.ccm")
        dlg0=wx.MessageDialog(None,u"字符表导出完毕!",u"KUON FONT TOOL",wx.OK)
        r=dlg0.ShowModal()
        dlg0.Destroy()

    def OnClick_exfont_info(self ,event):
        fonttool = Fonttool()
        fonttool.export_font_info("font.ccm")
        dlg0=wx.MessageDialog(None,u"字符索引导出完毕!",u"KUON FONT TOOL",wx.OK)
        r=dlg0.ShowModal()
        dlg0.Destroy()

    def OnClick_expng(self ,event):
        fonttool = Fonttool()
        fonttool.expng("standard.tm2")
        fonttool.expng("sjis.tm2")
        fonttool.expng("menu.tm2")
        dlg0=wx.MessageDialog(None,u"字库图导出完毕!",u"KUON FONT TOOL",wx.OK)
        r=dlg0.ShowModal()
        dlg0.Destroy()

    def OnClick_buildfont(self ,event):
        fonttool = Fonttool()
        value = fonttool.build_ccm("ccminfo.ini" , 1024 , 1024 , "cn\\font.big.csv" , "menu.ccm")
        value = fonttool.build_ccm("ccminfo.ini" , 1024 , 512 , "cn\\font.small.csv" , "sjis.ccm")
        value = fonttool.build_ccm("ccminfo.ini" , 1024 , 1024 , "cn\\font.color.csv" , "standard.ccm")
        msg = ""
        if value:
            msg = u"构建成功"
        else:
            msg = u"构建失败，字库超出范围，请重新设定高度"
        dlg0=wx.MessageDialog(None ,msg ,u"KUON FONT TOOL",wx.OK)
        r=dlg0.ShowModal()
        dlg0.Destroy()

    def __init__(self, parent, title = u"KUON FONT TOOL"):
        wx.Frame.__init__(self, parent, -1, title,pos=(150, 150), size=(400, 360))
        panel = wx.Panel(self, -1)
        self.button = wx.Button(panel, -1, u"导出字库图片", pos=(50, 20))
        wx.StaticText(panel ,-1 ,u"导出字库图片" ,(200, 20))
        self.Bind(wx.EVT_BUTTON, self.OnClick_expng,self.button)
        self.button.SetDefault()

        self.button1 = wx.Button(panel, -1, u"导出字符表", pos=(50, 60))
        wx.StaticText(panel ,-1 ,u"导出字符表" ,(200, 60))
        self.Bind(wx.EVT_BUTTON, self.OnClick_excharlist,self.button1)
        self.button1.SetDefault()

        self.button2 = wx.Button(panel, -1, u"导出字库索引", pos=(50, 100))
        wx.StaticText(panel ,-1 ,u"导出字库索引" ,(200, 100))
        self.Bind(wx.EVT_BUTTON, self.OnClick_exfont_info,self.button2)
        self.button2.SetDefault()

        self.button3 = wx.Button(panel, -1, u"创建字库索引", pos=(50, 140))
        wx.StaticText(panel ,-1 ,u"创建字库索引" ,(200, 140))
        self.Bind(wx.EVT_BUTTON, self.OnClick_buildfont,self.button3)
        self.button3.SetDefault()


        self.Show()
if __name__ == '__main__':
    app = wx.App(redirect=True)
    wxFont(None)
    app.MainLoop()
