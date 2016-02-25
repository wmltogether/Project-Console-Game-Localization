import codecs,os,glob,struct
def dir_fn(adr ,ext_name):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            ext = name.split('.')[-1]
            adrlist=os.path.join(root, name)
            if ext.lower() in ext_name:
                dirlst.append(adrlist)
    return dirlst
def find():
    fl = dir_fn('LAYOUT' , ['arc'])
    a = True
    for fn in fl:
        if a:
            fp = open(fn , 'rb')
            data = fp.read()
            dest = open('UNPACK\\%s'%fn.replace('\\' , '__') , 'wb')
            dest.write(data)
            dest.close()
            fp.close()
find()