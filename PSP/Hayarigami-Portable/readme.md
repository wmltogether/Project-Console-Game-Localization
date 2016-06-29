PSP Hayarigami Portable - Keishichou Kaii Jiken 

PSP 流行之神 1 汉化工具集

storytool.py  主脚本解析工具
occultfiletool.py 文档解析工具

这个游戏所有的字库和文本全部打包加密在start.dat中，
对话字符串经过0xff异或，并在内存中实时解密，所以在内存中只能搜到当前句子，无法搜索前后文。

字库修改方式


>//889F-9872

>//tile id从01b9 - 0d4d

>//地址从0xbfe - 0x23a6 ，2字节为一组id

>//从0xbfe之后的汉字部分完全符合这一规则

>>for j0 in xrange(0x81,0x99):

>>        for j1 in xrange(0x40,0x100):

>>            if ((j0  * 0x100) + j1) >= 0x889F and ((j0  * 0x100) + j1) <= 0x9872:

>>            

>>                    s_list.append( (j0  * 0x100) + j1)

>//这一区间总共可以容纳2965个汉字，

>//889F-9872与cp932完全重合，其他区域(20-7E 8140 - 889F )不重合，直接用原始数据抄上去

>//字库修改思路，FNT文件保留tile id 01b9（不包含01b9，地址是02h - 0BFEh）之前的所有字符，01b9（0BFEh - 23A6h）开始填充889F的汉字表

>//FTD文件是2字节为一组的kerning，数值为左起始坐标xoffset, 字符右侧增加对齐像素xadvance，汉字不需要这东西，全填0

>//FTX文件是tile，前10h为tile配置（tile_w, tile_h , ），10h - 410h为调色板（0x40为一组，一共10组），410h开始为tile数据

>//JIS2UCS为转码到unicode存档的文件，只修改889F之后的部分，剩余位置填充FFFF

>
