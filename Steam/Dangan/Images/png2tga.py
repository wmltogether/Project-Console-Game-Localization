from PIL import Image
import os,codecs,struct,traceback
from GIDecode import *
class TGA:
    def __init__(self):
        self.bHasComment = False
        self.bHasPalette = False
        self.bCompressed = False
        self.width = 0
        self.height = 0
        self.x_start = 0
        self.y_start = 0
        self.palette_color_index = 0
        self.palette_color_nums = 0
        self.palette_color_bits = 0
        self.filename = ""
        self.bpp = 0
        self.headerLength = 0

    def open(self , tga_name):
        self.filename = tga_name
        
    def getPNG_extinfo(self):
        name  = self.filename
        name = name.replace("pak_files\\" , "")
        name = name.replace("\\" , "__")
        name = name[:-4] + ".png"
        im = Image.open('cnpng\\%s'%name).convert('RGBA')
        im2 = im.transpose(Image.FLIP_TOP_BOTTOM)
        width,height=(im.size[0],im.size[1])
        return (width , height ,im2)
        
    def _get_tga8_info(self):
        bHasPalette = False
        fp = open(self.filename , "rb")
        a,b,c = struct.unpack("3B" , fp.read(3))
        if b == 0:
            self.bHasPalette = False
        elif b == 1:
            self.bHasPalette = True
        else:
            print("error:unrecongnized palette setting")
        if c == 0:
            self.bCompressed = False
        elif c == 1:
            self.bCompressed = True
        else:
            print("error:unrecongnized compress setting")
        self.palette_color_index,self.palette_color_nums = struct.unpack("2H" , fp.read(4))
        self.palette_color_bits = ord(fp.read(1))
        self.x_start ,self.y_start , self.width, self.height = struct.unpack("4H" , fp.read(8))
        self.bpp = struct.unpack("B" , fp.read(1))
        tmpbits = fp.read(1)
        self.headerLength = fp.tell()
        fp.close()

    def encode(self):
        fp = open(self.filename , "rb")
        fp.seek(self.headerLength , 0)
        datalist = []
        if self.bHasPalette == True:
            # yes it's a 8bpp encoded tga
            if self.palette_color_nums == 256 and self.palette_color_bits == 32:
                paldata = fp.read(0x400)
                palette_list = getPaletteData(paldata,256,4,False,0)
            if self.palette_color_nums == 256 and self.palette_color_bits == 24:
                paldata = fp.read(0x300)
                palette_list = getPaletteData(paldata,256,3,False,0)
            if self.palette_color_nums == 16 and self.palette_color_bits == 32:
                paldata = fp.read(0x40)
                palette_list = getPaletteData(paldata,16,4,False,0)
            if self.palette_color_nums == 16 and self.palette_color_bits == 24:
                paldata = fp.read(0x40)
                palette_list = getPaletteData(paldata,16,3,False,0)
            new_palette_list = palette_list
            for i in xrange(len(palette_list)):
                (r,g,b,a) = palette_list[i]
                new_palette_list[i] = (b,g,r,a)
            (width , height ,im) = self.getPNG_extinfo()
            imdata = create8BPP(width, height, width, height, im, 
                                               palette_list, 
                                               'linear', 
                                               0, 0)
            return paldata + imdata
        return ""

    def decode(self):
        fp = open(self.filename , "rb")
        fp.seek(self.headerLength , 0)
        datalist = []
        if self.bHasPalette == True:
            # yes it's a 8bpp encoded tga
            if self.palette_color_nums == 256 and self.palette_color_bits == 32:
                paldata = fp.read(0x400)
                palette_list = getPaletteData(paldata,256,4,False,0)
            if self.palette_color_nums == 256 and self.palette_color_bits == 24:
                paldata = fp.read(0x300)
                palette_list = getPaletteData(paldata,256,3,False,0)
            if self.palette_color_nums == 16 and self.palette_color_bits == 32:
                paldata = fp.read(0x40)
                palette_list = getPaletteData(paldata,16,4,False,0)
            if self.palette_color_nums == 16 and self.palette_color_bits == 24:
                paldata = fp.read(0x40)
                palette_list = getPaletteData(paldata,16,3,False,0)
            new_palette_list = palette_list
            for i in xrange(len(palette_list)):
                (r,g,b,a) = palette_list[i]
                new_palette_list[i] = (b,g,r,a)
            data = fp.read(self.width * self.height)
            datalist = paint8BPP(self.width ,
                      self.height,
                      self.width,
                      self.height,data,new_palette_list,"liner",
                      256,"win32")
        return datalist
    
    def save(self , dest_name):
        self._get_tga8_info()
        data = self.encode()
        if len(data) > 0:
            print("save to>>%s"%dest_name)
            img = open(dest_name , "rb+")
            img.seek(self.headerLength)
            img.write(data)
            img.close()

def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst

fl = dir_fn("cnpng")
for fn in fl:
    if fn[-4:].lower() == ".png":
        tga_tool = TGA()
        if "pak_bin__pak_files__bin" in fn:
            tmp = fn.split("\\")[-1][:-4]
            tga_name = tmp.split("__")[0] + "\\" + "__".join(tmp.split("__")[1:-1]) + "\\" + tmp.split("__")[-1] + '.tga'
            tga_tool.open("%s"%tga_name)
            print(fn)
            dest_name = fn
            tga_tool.save("%s"%tga_name)
        else:
            tga_name = fn.split("\\")[-1][:-4].replace("__" , "\\") + '.tga'
            tga_tool.open("pak_files\\%s"%tga_name)
            print(fn)
            dest_name = fn
            tga_tool.save("pak_files\\%s"%tga_name)


