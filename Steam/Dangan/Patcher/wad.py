# -*- coding:utf-8 -*-
import codecs,os,struct
from System.Windows.Forms import *
from util import *
class WAD:
	def __init__(self):
		self.filename = ""
		self.patch_folder = "patch"
		self.magic = "AGAR"

	def _get_file_dict(self):
		fp = open(self.filename , "rb")
		sig = fp.read(4)
		if sig != self.magic:
			return {}
		waddict = {}
		wadinfo = []
		fp.seek(0x10,0)
		nums = struct.unpack("I" , fp.read(4))[0]
		for i in xrange(nums):
			fname_size = struct.unpack("I",fp.read(4))[0]
			fname = fp.read(fname_size)
			i_pos = fp.tell()
			fsize = struct.unpack("Q",fp.read(8))[0]
			foffset = struct.unpack("Q",fp.read(8))[0]
			wadinfo.append((fname , foffset , fsize , i_pos))
		pos = fp.tell()
		print("%08x"%fp.tell())
		mp_pos = pos
		if "dr1_data_keyboard.wad" in self.filename:
			tmp_pos = 0xbb3
		if "dr1_data.wad" in self.filename:
			tmp_pos = 0x1CFE67
		for i in xrange(len(wadinfo)):
			(fname , foffset , fsize , fsize_pos) = wadinfo[i]
			waddict[fname] = (foffset + tmp_pos , fsize , fsize_pos)
		fp.close()
		return waddict

	def _get_wad_info(self):
		fp = open(self.filename , "rb")
		sig = fp.read(4)
		if sig != self.magic:
			return []
		wadinfo = []
		fp.seek(0x10,0)
		nums = struct.unpack("I" , fp.read(4))[0]
		for i in xrange(nums):
			fname_size = struct.unpack("I",fp.read(4))[0]
			fname = fp.read(fname_size)
			i_pos = fp.tell()
			fsize = struct.unpack("Q",fp.read(8))[0]
			foffset = struct.unpack("Q",fp.read(8))[0]
			wadinfo.append((fname , foffset , fsize , i_pos))
		pos = fp.tell()
		print("%08x"%fp.tell())
		mp_pos = pos
		if "dr1_data_keyboard.wad" in self.filename:
			tmp_pos = 0xbb3
		if "dr1_data.wad" in self.filename:
			tmp_pos = 0x1CFE67
		for i in xrange(len(wadinfo)):
			(fname , foffset , fsize , fsize_pos) = wadinfo[i]
			wadinfo[i] = (fname , foffset + tmp_pos , fsize , fsize_pos)
		fp.close()
		return wadinfo

	def _unpack_wad(self):
		wadinfo = self._get_wad_info()
		fp = open(self.filename , "rb")
		for i in xrange(len(wadinfo)):
			(fname , foffset , fsize , fsize_pos) = wadinfo[i]
			dirname = os.path.dirname("%s_unpacked\\%s"%(self.filename , fname))
			if not os.path.exists(dirname):
				os.makedirs(dirname)
			dest = open("%s_unpacked\\%s"%(self.filename , fname) , "wb")
			fp.seek(foffset)
			data = fp.read(fsize)
			dest.write(data)
			dest.close()
		fp.close()
	
	def _patch_wad(self):
		if not os.path.exists(self.patch_folder):
			MessageBox.Show("Error:Patch folder not found.\nPlease set the Patch folder.")
		if not os.path.exists(self.filename):
			MessageBox.Show("Error:Archive not found.")
		dict = self._get_file_dict()
		fl = dir_fn(self.patch_folder)
		dest = open(self.filename , "rb+")
		dest.seek(0)
		sig = dest.read(4)
		tmp_pos = 0x1CFE67
		if "dr1_data_keyboard.wad" in self.filename:
			tmp_pos = 0xbb3
		if "dr1_data.wad" in self.filename:
			tmp_pos = 0x1CFE67
		if sig != self.magic:
			MessageBox.Show("Error:Archive Header Error!\nNot a WAD Pack.")
			return None
		s_nums = 0
		for fn in fl:
			pname = fn[len(self.patch_folder):]
			pname = pname.replace("\\" ,"/")
			print(pname)
			if pname[0] == "/":pname = pname[1:]
			if pname in dict:
				s_nums += 1
				print("patching :%s"%pname)
				pfile = open(fn , "rb")
				pdata = pfile.read()
				dsize = len(pdata)
				(foffset , fsize , fsize_pos) = dict[pname]
				if fsize >= dsize:
					print("USE INJECT METHOD")
					dest.seek(foffset)
					dest.write(pdata)
					dest.write("\x00" * (fsize - dsize))
					dest.seek(fsize_pos)
					dest.write(struct.pack("I" , dsize))
					dest.write(struct.pack("I" , 0))
					dest.write(struct.pack("I" , foffset - tmp_pos))
				
				else:
					print("USE EXTEND METHOD")
					dest.seek(0,2)
					end_pos = dest.tell()
					dest.seek(end_pos)
					dest.write(pdata)
					dest.seek(fsize_pos)
					dest.write(struct.pack("I" , dsize))
					dest.write(struct.pack("I" , 0))
					dest.write(struct.pack("I" , end_pos - tmp_pos))
					
				pfile.close()
		dest.close()
		return s_nums
		
				
				
			
		
