# -*- coding: cp936 -*-
import codecs,os
import glob,struct
def count_char(string,char):
    p=0
    for i in range(len(string)):
        if string[i]==char:
            p+=1
        else:
            pass
    return p
def makestr(lines):
    string_list = []
    head_list = []
    num = len(lines)
    for index,line in enumerate(lines):
        if u'####' in line:
            head_list.append(line[5:-7])
            i = 1
            string = ''
            while True:
                if index+i >= num:
                    break
                if '####' in lines[index+i]:
                    break
                string += lines[index+i]
                i += 1
            string_list.append(string[:-4])
    return string_list, head_list
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def import_text(fn):
    f=open('text\\%s'%fn,'rb')
    clines=codecs.open('cntext\\%s.jp.txt'%fn,'rb','utf-16').readlines()
    jlines=codecs.open('jptext/%s.jp.txt'%fn,'rb','utf-16').readlines()
    clist, head_list=makestr(clines)
    jlist, j_head_list=makestr(jlines)
    eng_lines=f.read()[4:].decode('utf-8').split(r'};')
    for i in range(len(clist)):
        cstring=clist[i]
        jstring=jlist[i].replace('\r\n','')
        chead=int(head_list[i])
        cstring=cstring.replace('\r\n','')
        p_c=count_char(cstring,r'"')
        p_j=count_char(jstring,r'"')
        if p_c != p_j:
            print('%s\r\n%s'%(jstring,cstring))
        p_c=count_char(cstring,r'>')
        p_j=count_char(jstring,r'>')
        if p_c != p_j:
            print('%s\r\n%s'%(jstring,cstring))          
        eng_text=eng_lines[chead]
        eng_text=eng_text.replace(jstring,cstring)
        eng_lines[chead]=eng_text
    dest=open('import\\%s'%fn,'wb')
    data1=(r'};'.join(eng_lines)).encode('utf-8')
    dest.write(struct.pack('>I',len(data1)))
    dest.write(data1)
    dest.close()
    f.close()
fl=dir_fn('cntext')
for fn in fl:
    print(fn[7:])
    if fn[7:][-4:].lower()=='.txt':
        import_text(fn[7:-7])
