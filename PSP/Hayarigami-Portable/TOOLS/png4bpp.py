from GIDecode import *

fp = open("FONTA.FTX" , "rb")
fp.seek(0x10)
paldata = fp.read(0x40)
palList = getPaletteData(paldata,0xff , 4 ,False , 0)
im = Image.open("font.png" ).convert('RGBA')
m_width,m_height=(im.size[0],im.size[1])
data = create4BPP(m_width , m_height , 24 ,24, im ,palList , "BIG")
dest = open("font.bin" , "wb")
dest.write(data)
dest.close()

fp.close()
