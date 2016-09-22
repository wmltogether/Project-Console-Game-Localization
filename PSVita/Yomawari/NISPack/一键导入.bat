@echo off
@echo 夜廻一键导入工具
if exist "data.arc" (echo ok ) else (
	echo data.arc不存在，无法注入文本
	pause
	exit
)
python text_import.py
NISFONTBuilder.exe
rmdir /s/q patch
mkdir patch
@echo 请修改import目录中的tga文件为8位tga，按任意键进行导入
xcopy image\*.* patch\ /s /h /d /c /y
xcopy import\*.* patch\ /s /h /d /c /y
pause
arc_patcher.py
@echo 文本已经注入到data.arc中，请通过ftp将data.arc和eboot.bin复制到psv主机
pause