# -*- coding: utf-8 -*-
from ubi_ipk import unpack_ipk
import sys
import traceback
def main():
    unpack_ipk('bundle_ps3.ipk')

if __name__=='__main__':
    if sys.version_info < (3, 0):
        print('Python 2.7 Ok')
        try:
            main()
        except:
            traceback.print_exc()
    else:
        print('You are using Python 3.x now，please install python 2.7')
    os.system('pause')
