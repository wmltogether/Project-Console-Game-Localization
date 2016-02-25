import codecs
from GIDecode import *
from PIL import Image,ImageColor
im = Image.open("cn\\font.color.Png").convert('RGBA')
fp = open("build\\standard.tm2" , "rb+")
fp.seek(0x20)
fp.seek(1024 * 1024 / 2 ,1)
palette_data = fp.read(0x40)
width,height=(im.size[0],im.size[1])
palette_list = getPaletteData(palette_data , \
                                              0x80 , 4 , False , 0 )
imdata = create4BPP(width, height, width, height, im,
                                               palette_list[:16],
                                               'BIG')
fp.seek(0x20)
fp.write(imdata)
fp.close()


im = Image.open("cn\\font.big.Png").convert('RGBA')
fp = open("build\\menu.tm2" , "rb+")
fp.seek(0x20)
fp.seek(1024 * 1024 / 2 ,1)
palette_data = fp.read(0x40)
width,height=(im.size[0],im.size[1])
palette_list = getPaletteData(palette_data , \
                                              0x80 , 4 , False , 0 )
imdata = create4BPP(width, height, width, height, im,
                                               palette_list[:16],
                                               'BIG')
fp.seek(0x20)
fp.write(imdata)
fp.close()

im = Image.open("cn\\font.small.Png").convert('RGBA')
fp = open("build\\sjis.tm2" , "rb+")
fp.seek(0x20)
fp.seek(1024 * 512 / 2 ,1)
palette_data = fp.read(0x40)
width,height=(im.size[0],im.size[1])
palette_list = getPaletteData(palette_data , \
                                              0x80 , 4 , False , 0 )
imdata = create4BPP(width, height, width, height, im,
                                               palette_list[:16],
                                               'BIG')
fp.seek(0x20)
fp.write(imdata)
fp.close()