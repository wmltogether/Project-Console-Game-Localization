import codecs,struct
import os
def export_loc8(fn):
    fp = open(fn,'rb')
    
    nums = struct.unpack('>I',fp.read(4))[0]
    for i in range(nums):
        language_id = struct.unpack('>I',fp.read(4))[0]
        print('    a_dict[%d] = %d'%(i,language_id))
        string_nums = struct.unpack('>I',fp.read(4))[0]
        #dest=codecs.open('%s.%d.txt'%(fn,i),'wb','utf-8')
        for j in range(string_nums):
            unk0 = struct.unpack('>I',fp.read(4))[0]
            string_length = struct.unpack('>I',fp.read(4))[0]
            string = fp.read(string_length).decode('utf-8')
            string = string.replace('\n','\r\n')
            #dest.write('#### %d,%d ####\r\n%s\r\n\r\n'%(j,unk0,string))
        #dest.close()   
    fp.close()
export_loc8('localisation.loc8')
