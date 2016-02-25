# -*- coding: utf-8 -*-
import System.Drawing
import System.Windows.Forms

from System.Drawing import *
from System.Windows.Forms import *
from System.IO import *
import wad
class MainForm(Form):
	def __init__(self):
		self.InitializeComponent()
	
	def InitializeComponent(self):
		self._buttonPatchFile = System.Windows.Forms.Button()
		self._textBoxMainPath = System.Windows.Forms.TextBox()
		self._buttonSelectMainFile = System.Windows.Forms.Button()
		self._label1 = System.Windows.Forms.Label()
		self._label2 = System.Windows.Forms.Label()
		self._textBoxSubPath = System.Windows.Forms.TextBox()
		self._buttonSelectSubFile = System.Windows.Forms.Button()
		self._label3 = System.Windows.Forms.Label()
		self._label4 = System.Windows.Forms.Label()
		self._textBoxExePath = System.Windows.Forms.TextBox()
		self._buttonSelectExePath = System.Windows.Forms.Button()
		self.SuspendLayout()
		# 
		# buttonPatchFile
		# 
		self._buttonPatchFile.Location = System.Drawing.Point(180, 276)
		self._buttonPatchFile.Name = "buttonPatchFile"
		self._buttonPatchFile.Size = System.Drawing.Size(117, 35)
		self._buttonPatchFile.TabIndex = 0
		self._buttonPatchFile.Text = "Start Patch!"
		self._buttonPatchFile.UseVisualStyleBackColor = True
		self._buttonPatchFile.Click += self.ButtonPatchFileClick
		# 
		# textBoxMainPath
		# 
		self._textBoxMainPath.Location = System.Drawing.Point(21, 72)
		self._textBoxMainPath.Name = "textBoxMainPath"
		self._textBoxMainPath.Size = System.Drawing.Size(366, 21)
		self._textBoxMainPath.TabIndex = 1
		# 
		# buttonSelectMainFile
		# 
		self._buttonSelectMainFile.Location = System.Drawing.Point(393, 70)
		self._buttonSelectMainFile.Name = "buttonSelectMainFile"
		self._buttonSelectMainFile.Size = System.Drawing.Size(29, 23)
		self._buttonSelectMainFile.TabIndex = 2
		self._buttonSelectMainFile.Text = "..."
		self._buttonSelectMainFile.UseVisualStyleBackColor = True
		self._buttonSelectMainFile.Click += self.ButtonSelectMainFileClick
		# 
		# label1
		# 
		self._label1.Location = System.Drawing.Point(21, 51)
		self._label1.Name = "label1"
		self._label1.Size = System.Drawing.Size(161, 20)
		self._label1.TabIndex = 3
		self._label1.Text = "Select dr1_data.wad"
		# 
		# label2
		# 
		self._label2.Location = System.Drawing.Point(21, 106)
		self._label2.Name = "label2"
		self._label2.Size = System.Drawing.Size(262, 23)
		self._label2.TabIndex = 4
		self._label2.Text = "Select dr1_data_keyboard.wad"
		# 
		# textBoxSubPath
		# 
		self._textBoxSubPath.Location = System.Drawing.Point(21, 133)
		self._textBoxSubPath.Name = "textBoxSubPath"
		self._textBoxSubPath.Size = System.Drawing.Size(366, 21)
		self._textBoxSubPath.TabIndex = 5
		# 
		# buttonSelectSubFile
		# 
		self._buttonSelectSubFile.Location = System.Drawing.Point(393, 133)
		self._buttonSelectSubFile.Name = "buttonSelectSubFile"
		self._buttonSelectSubFile.Size = System.Drawing.Size(29, 23)
		self._buttonSelectSubFile.TabIndex = 6
		self._buttonSelectSubFile.Text = "..."
		self._buttonSelectSubFile.UseVisualStyleBackColor = True
		self._buttonSelectSubFile.Click += self.ButtonSelectSubFileClick
		# 
		# label3
		# 
		self._label3.ForeColor = System.Drawing.Color.Blue
		self._label3.Location = System.Drawing.Point(319, 314)
		self._label3.Name = "label3"
		self._label3.Size = System.Drawing.Size(151, 16)
		self._label3.TabIndex = 7
		self._label3.Text = "http://www.pujia8.com"
		# 
		# label4
		# 
		self._label4.Location = System.Drawing.Point(21, 175)
		self._label4.Name = "label4"
		self._label4.Size = System.Drawing.Size(180, 23)
		self._label4.TabIndex = 8
		self._label4.Text = "Select DR1_us.exe"
		# 
		# textBoxExePath
		# 
		self._textBoxExePath.Location = System.Drawing.Point(21, 202)
		self._textBoxExePath.Name = "textBoxExePath"
		self._textBoxExePath.Size = System.Drawing.Size(366, 21)
		self._textBoxExePath.TabIndex = 9
		# 
		# buttonSelectExePath
		# 
		self._buttonSelectExePath.Location = System.Drawing.Point(394, 202)
		self._buttonSelectExePath.Name = "buttonSelectExePath"
		self._buttonSelectExePath.Size = System.Drawing.Size(28, 23)
		self._buttonSelectExePath.TabIndex = 10
		self._buttonSelectExePath.Text = "..."
		self._buttonSelectExePath.UseVisualStyleBackColor = True
		self._buttonSelectExePath.Click += self.ButtonSelectExePathClick
		# 
		# MainForm
		# 
		self.ClientSize = System.Drawing.Size(492, 339)
		self.Controls.Add(self._buttonSelectExePath)
		self.Controls.Add(self._textBoxExePath)
		self.Controls.Add(self._label4)
		self.Controls.Add(self._label3)
		self.Controls.Add(self._buttonSelectSubFile)
		self.Controls.Add(self._textBoxSubPath)
		self.Controls.Add(self._label2)
		self.Controls.Add(self._label1)
		self.Controls.Add(self._buttonSelectMainFile)
		self.Controls.Add(self._textBoxMainPath)
		self.Controls.Add(self._buttonPatchFile)
		self.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedToolWindow
		self.Name = "MainForm"
		self.Text = "PCDanganPatcher(v1.0)"
		self.ResumeLayout(False)
		self.PerformLayout()


	def ButtonSelectMainFileClick(self, sender, e):
		dialog = OpenFileDialog()
		dialog.Filter = "Dangan WAD# files (*.wad)|*.wad"
		if dialog.ShowDialog(self) == DialogResult.OK:
			self._textBoxMainPath.Text = dialog.FileName
		pass
	
	def ButtonSelectSubFileClick(self, sender, e):
		dialog = OpenFileDialog()
		dialog.Filter = "Dangan WAD# files (*.wad)|*.wad"
		if dialog.ShowDialog(self) == DialogResult.OK:
			self._textBoxSubPath.Text = dialog.FileName
		pass

	def ButtonPatchFileClick(self, sender, e):
		wadpack = wad.WAD()
		wadpack.filename = self._textBoxMainPath.Text
		snums_main = 0
		snums_sub = 0
		if File.Exists(wadpack.filename):
			# patching main
			snums_main = wadpack._patch_wad()
		wadpack.filename = self._textBoxSubPath.Text
		if File.Exists(wadpack.filename):
			# patching main
			snums_sub = wadpack._patch_wad()
		self.exename = self._textBoxExePath.Text
		if File.Exists(self.exename) and File.Exists("patch\\EBOOT.BIN"):
			import util
			util.patch_eboot(self.exename , "patch\\EBOOT.BIN")
		MessageBox.Show("Patch Successed:\n%d file Patched in dr1_data.wad.\n%d file Patched in dr1_data_keyboard.wad.\n!"%(snums_main ,snums_sub))
		pass
	

	def ButtonSelectExePathClick(self, sender, e):
		dialog = OpenFileDialog()
		dialog.Filter = "Dangan EXE# files (*.exe)|*.exe"
		if dialog.ShowDialog(self) == DialogResult.OK:
			self._textBoxExePath.Text = dialog.FileName
		pass
