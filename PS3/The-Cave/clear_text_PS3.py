import codecs,os
def clear_main_text(fn):
    f=open(fn,'rb')
    lines=f.read()[4:].decode('utf-8').split(r'};')
    dest=codecs.open('jptext\\cave_jajp.jp.txt','wb','utf-16')
    for i in range(len(lines)):
        if 'Text=' in lines[i]:
            line=lines[i]
            #print(i)
            text0=line.split(r'Text=')[1]
            if ';' in text0:
                sLine=text0.split(';')[0]
                sLine=sLine.replace('<br>','<br>\r\n')
                dest.write('#### %d ####\r\n%s\r\n\r\n'%(i,sLine))
    f.close()
    dest.close()
            
clear_main_text('cave_jajp')
