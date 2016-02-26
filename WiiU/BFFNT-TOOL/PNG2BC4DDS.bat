AMDCompressCLI.exe -nomipmap -fd BC4 inPNG/font.0.Png inDDS/font.0.dds
AMDCompressCLI.exe -nomipmap -fd BC4 inPNG/font.1.Png inDDS/font.1.dds
AMDCompressCLI.exe -nomipmap -fd BC4 inPNG/font.2.Png inDDS/font.2.dds
AMDCompressCLI.exe -nomipmap -fd BC4 inPNG/font.3.Png inDDS/font.3.dds
AMDCompressCLI.exe -nomipmap -fd BC4 inPNG/font.4.Png inDDS/font.4.dds
AMDCompressCLI.exe -nomipmap -fd BC4 inPNG/font.5.Png inDDS/font.5.dds
AMDCompressCLI.exe -nomipmap -fd BC4 inPNG/font.6.Png inDDS/font.6.dds

TexConv2.exe -i inDDS/font.0.dds -o inGTX/font.0.gtx -swizzle 0
TexConv2.exe -i inDDS/font.1.dds -o inGTX/font.1.gtx -swizzle 2
TexConv2.exe -i inDDS/font.2.dds -o inGTX/font.2.gtx -swizzle 4
TexConv2.exe -i inDDS/font.3.dds -o inGTX/font.3.gtx -swizzle 6
TexConv2.exe -i inDDS/font.4.dds -o inGTX/font.4.gtx -swizzle 8
TexConv2.exe -i inDDS/font.5.dds -o inGTX/font.5.gtx -swizzle 10
TexConv2.exe -i inDDS/font.6.dds -o inGTX/font.6.gtx -swizzle 12

pause
