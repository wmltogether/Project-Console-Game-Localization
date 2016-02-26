使用举例：
1.使用bffnt2DDS.py可以将bffnt文件转换成dds文件
2.使用bffnt2charlist.exe可以讲bffnt文件内部的字符表导出
3.假设要制作一个LENS5_SYSTEM_FONT.BFFNT的字库
4.设计一个新字符表，命名为LENS5_SYSTEM_FONT.BFFNT_charlist.txt
5.根据LENS5_SYSTEM_FONT.BFFNT_charlist.txt，使用TiledGlyph（https://github.com/wmltogether/TiledGlyph）创建新的字库图和message.bin索引文件，字库参数可以在TiledGlyph里设置。
6.使用PNG2BC4DDS.bat构建swizzle过的新gtx数据
7.使用bffntBuilder.py构建新的bffnt字库，字库参数需要在bffntBuilder.py内部设置

