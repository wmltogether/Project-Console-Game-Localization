# -*- coding:utf-8 -*-
import codecs,fnmatch,struct,os
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

def make_font(csv_name , dest_font_name , base_hax):
    data_list = csv2data(csv_name)
    dest = open(dest_font_name , "wb")
    dest.write("tFpS")
    dest.write(struct.pack("I" ,4))
    dest.write(struct.pack("I" ,len(data_list)))
    dest.write(struct.pack("I" ,(data_list[-1][0] + 1) * 2 + 0x20))
    dest.write(struct.pack("I" ,data_list[-1][0] + 1))
    dest.write(struct.pack("I" ,data_list[0][0]))
    dest.write(struct.pack("I" ,base_hax))
    dest.write(struct.pack("I" ,1))
    dest.write("\xFF\xFF" * (data_list[-1][0] + 1))
    dest.write("\x00" * (10 * len(data_list)))
    print(len(data_list))
    for i in xrange(len(data_list)):
        (char_code ,x,y,char_width,char_height) = data_list[i]
        dest.seek(0x20 + char_code * 2)
        dest.write(struct.pack("H" , i))
        dest.seek((data_list[-1][0] + 1) * 2 + 0x20 + 0x10 * i)
        dest.write(struct.pack("H" , char_code))
        dest.write(struct.pack("H" , x))
        dest.write(struct.pack("H" , y))
        dest.write(struct.pack("H" , char_width))
        dest.write(struct.pack("H" , char_height))
        dest.write(struct.pack("H" , 0))
        dest.write(struct.pack("H" , 0))
        dest.write(struct.pack("H" , 0))
    dest.close()



make_font("build\\normal_font.csv" , "font\\font\\0001.tfps" , 0x49)
make_font("build\\big_font.csv" , "font\\font\\0003.tfps" , 0x91)


