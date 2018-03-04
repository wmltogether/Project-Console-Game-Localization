using System;
using System.Collections.Generic;
using System.Data.Common;
using System.Linq;
using System.Text;
using System.IO;
using AtlusGames.Extension;


namespace AtlusGames.GameFormat
{
    public class DDT
    {
        public string ImgName = "";
        public string DDTName = "";
        private string tmpFolder = "";
        private Dictionary<string, Entry> fDictionary = new Dictionary<string, Entry>(StringComparer.OrdinalIgnoreCase);
        public List<Entry> Entries
        {
            get { return mEntries; }
        }
        private List<Entry> mEntries = new List<Entry>();

        public DDT(string imgName,string ddtName)
        {
            ImgName = imgName;
            DDTName = ddtName;

        }


        public void GetEntry()
        {
            fDictionary = new Dictionary<string, Entry>();
            FileStream fs = File.OpenRead(this.DDTName); 
            BinaryReader br = new BinaryReader(fs);
            this._getEntry(ref br, this.tmpFolder);
            for (int i = 0; i < this.mEntries.Count; i++)
            {
                Entry vEntry = this.mEntries[i];
                string vKey = vEntry.FullName;
                if (!fDictionary.ContainsKey(vKey))
                {
                    fDictionary.Add(vKey, vEntry);
                }
                else
                {
                    fDictionary[vKey] = vEntry;
                }
            }

        }

        private void _getEntry(ref BinaryReader br, string folder)
        {
            int pos = (int) br.BaseStream.Position;
            int name_off = br.ReadInt32();
            int offset = br.ReadInt32();
            int size = br.ReadInt32();
            br.BaseStream.Seek(name_off, SeekOrigin.Begin);
            string name = br.ReadCString();

            folder = folder + "/";
            folder = folder + name;
            if (size < 0)
            {
                br.BaseStream.Seek(offset, SeekOrigin.Begin);
                int folders = Math.Abs(size);
                for (int i = 0; i < folders; i++)
                {
                    this._getEntry(ref br, folder);
                }
            }
            else
            {
                Entry vEntry = new Entry();
                vEntry.Offset = offset * 0x800;
                vEntry.Size = size;
                vEntry.Ptr = pos;
                vEntry.FullName = folder.Replace("//","/");
                this.mEntries.Add(vEntry);
            }

            br.BaseStream.Seek(pos + 0xc, SeekOrigin.Begin);
        }

        public void Repack(string srcFolder, string patchFolder, string importFolder)
        {
            Logger.Print("正在读取索引数据");
            DDTFileTable table = JsonHelper.Deserialize<DDTFileTable>(File.ReadAllText("./dds3_table.json",Encoding.UTF8));
            this.GetEntry();
            Logger.Print("正在复制package");
            if (File.Exists(Path.Combine(importFolder, Path.GetFileName(this.ImgName))))
            {
                File.Delete(Path.Combine(importFolder, Path.GetFileName(this.ImgName)));
            }
            if (File.Exists(Path.Combine(importFolder, Path.GetFileName(this.DDTName))))
            {
                File.Delete(Path.Combine(importFolder, Path.GetFileName(this.DDTName)));
            }

            IOHelper.CopyFile(this.ImgName, Path.Combine(importFolder, Path.GetFileName(this.ImgName)));
            IOHelper.CopyFile(this.DDTName, Path.Combine(importFolder, Path.GetFileName(this.DDTName)));
            Logger.Print("开始对资源打补丁");
            List<string> pFileList = SearchPatchingFiles(table, patchFolder);
            Logger.Print(string.Format("有 {0} 个资源文件需要打补丁", pFileList.Count));


            FileStream imgStream = File.Open(Path.Combine(importFolder, Path.GetFileName(this.ImgName)),
                FileMode.Open, FileAccess.ReadWrite);
            FileStream ddtStream = File.Open(Path.Combine(importFolder, Path.GetFileName(this.DDTName)),
                FileMode.Open, FileAccess.ReadWrite);
            BinaryWriter imgWriter = new BinaryWriter(imgStream);
            BinaryWriter ddtWriter = new BinaryWriter(ddtStream);

            Entry vEntry;
            SubFile vSubFile;
            for (int i = 0; i < pFileList.Count; i++)
            {
                if (fDictionary.ContainsKey(pFileList[i]))
                {
                    byte[] data = null;

                    vEntry = fDictionary[pFileList[i]];
                    vSubFile = tempSubFileDictionary[pFileList[i]];
                    if (Path.GetExtension(vSubFile.FileName).ToLower().Equals(".lb")
                        && vSubFile.SubItems.Count > 0)
                    {
                        //lb包有子文件，启动压缩
                        LB lbContainer = new LB();
                        byte[] packedBytes = lbContainer.Repack(getBaseDir(vSubFile.FileName), vSubFile.FileName, srcFolder, patchFolder, vSubFile.SubItems);
                        //File.WriteAllBytes("temp/" + Path.GetFileName(vSubFile.FileName), packedBytes);
                        data = packedBytes;
                    }
                    else
                    {
                        string tmpPath = "";
                        if (File.Exists(patchFolder + "/"+ vSubFile.FileName))
                        {
                            tmpPath = patchFolder + "/" + vSubFile.FileName;
        }
                        else
                        {
                            tmpPath = srcFolder + "/" + vSubFile.FileName;
                        }

                        data = File.ReadAllBytes(tmpPath);
                    }

                    if (data != null)
                    {
                        var t_length = data.Length;
                        var chunk_size = 0;
                        if ((t_length % 0x800) == 0)
                        {
                            chunk_size = t_length;
                        }
                        else
                        {
                            chunk_size = t_length + 0x800 - t_length % 0x800;
                        }

                        var o_chunk_sz = 0;
                        if ((vEntry.Size % 0x800) == 0)
                        {
                            o_chunk_sz = vEntry.Size;
                        }
                        else
                        {
                            o_chunk_sz = vEntry.Size + 0x800 - vEntry.Size % 0x800;
                        }

                        if (chunk_size > o_chunk_sz)
                        {
                            //追加补丁
                            imgWriter.Seek(0, SeekOrigin.End);
                            var offset = imgWriter.BaseStream.Position / 0x800;
                            Logger.Print(string.Format("Append res file{0} to offfset {1:x8}", vSubFile.FileName,
                                offset * 0x800, t_length));
                            imgWriter.Write(data);
                            imgWriter.AlignPosition(0x800);
                            ddtWriter.Seek(vEntry.Ptr, SeekOrigin.Begin);
                            ddtWriter.Seek(4, SeekOrigin.Current);
                            ddtWriter.Write((int)offset);
                            ddtWriter.Write((int)t_length);


                        }
                        else
                        {
                            //原位替换
                            imgWriter.Seek(vEntry.Offset,SeekOrigin.Begin);
                            imgWriter.Write(Enumerable.Repeat((byte)0, vEntry.Size).ToArray());
                            imgWriter.Seek(vEntry.Offset, SeekOrigin.Begin);
                            var offset = vEntry.Offset / 0x800;
                            Logger.Print(string.Format("overrite res file{0} to offfset {1:x8}", vSubFile.FileName,
                                offset * 0x800, t_length));
                            imgWriter.Write(data);
                            ddtWriter.Seek(vEntry.Ptr, SeekOrigin.Begin);
                            ddtWriter.Seek(4, SeekOrigin.Current);
                            ddtWriter.Write((int)offset);
                            ddtWriter.Write((int)t_length);


                        }
                    }
                }
                
            }
            imgWriter.Close();
            ddtWriter.Close();
            Logger.Print("补丁结束。Have Fun");

        }

        private string getBaseDir(string path)
        {
            string[] p = path.Split('/');
            StringBuilder builder = new StringBuilder();
            for (int i = 0; i < p.Length - 1; i++)
            {    
                builder.Append(p[i]);
                builder.Append("/");
            }

            return builder.ToString();

        }

        private Dictionary<string, SubFile> tempSubFileDictionary = new Dictionary<string, SubFile>(StringComparer.OrdinalIgnoreCase);

        private List<string> SearchPatchingFiles(DDTFileTable table, string patchFolder)
        {
            List<string> fileList = new List<string>();
            bool hasChild = false;
            SubFile subFile;
            SubItem subItem;
            string path;
            for (int i=0;i< table.Files.Count;i++)
            {
                subFile = table.Files[i];
                path = (patchFolder + subFile.FileName).Replace("//", "/");
                if (!tempSubFileDictionary.ContainsKey(subFile.FileName))
                {
                    tempSubFileDictionary.Add(subFile.FileName, subFile);
                }
                if (File.Exists(path))
                {
                    fileList.Add(subFile.FileName);
                }

                hasChild = false;
                for (int j= 0; j < subFile.SubItems.Count; j++)
                {
                    subItem = subFile.SubItems[j];
                    path = (getBaseDir(path) + "/" + subItem.FileName).Replace("//", "/");
                    if (File.Exists(path))
                    {
                        hasChild = true;
                        break;
                    }
                }

                if (hasChild && (!fileList.Contains(subFile.FileName)))
                {
                    fileList.Add(subFile.FileName);
                }
            }

            return fileList;
        }


        public void Extract(string pathName)
        {
            DDTFileTable table = new DDTFileTable();
            this.GetEntry();

            using (FileStream fs = File.OpenRead(this.ImgName))
            {
                using (BinaryReader br = new BinaryReader(fs))
                {
                    for (int i = 0; i < this.mEntries.Count; i++)
                    {
                        Entry vEntry = mEntries[i];
                        
                        
                        string dstPath = pathName + "/" + vEntry.FullName;
                        string dirname = Path.GetDirectoryName(dstPath);
                        var vSubItems = new List<SubItem>();
                        br.BaseStream.Seek(vEntry.Offset, SeekOrigin.Begin);
                        byte[] entryData = br.ReadBytes(vEntry.Size);
                        Logger.Print(string.Format("{0}:at offset:{1:x8}", vEntry.FullName, vEntry.Offset));
                        if (!Directory.Exists(dirname))
                        {
                            Directory.CreateDirectory(dirname);
                        }

                        using (FileStream entrFile = File.OpenWrite(dstPath))
                        {
                            entrFile.Write(entryData, 0, entryData.Length);
                        }

                        //如果是lb，则额外进行解包操作。
                        if (Path.GetExtension(vEntry.FullName).ToLower().Equals(".lb"))
                        {
                            LB lbPackage = new LB();
                            lbPackage.Load(dstPath);
                            vSubItems = lbPackage.SubItems;
                            for(int p=0;p<lbPackage.SubItems.Count;p++)
                            {
                                var vitem = lbPackage.SubItems[p];
                                var tExt = Path.GetExtension(vitem.FileName).ToLower();
                                if (tExt.Equals(".bf")
                                    || tExt.Equals(".tmx")
                                    /*|| Path.GetExtension(vitem.FileName).ToLower().Equals(".pac")*/)
                                {
                                    //如果是bf和tmx，则设定为解包并解压。
                                    Logger.Print(string.Format("\t- Extract {0}", vitem.FileName));
                                    byte[] zipdata = lbPackage.Unpack(vitem.FileName);
                                    string dstName = Path.Combine(dirname, vitem.FileName);
                                    if (vSubItems[p].IsCompressed)
                                    {
                                        vSubItems[p].NeedReCompress = true;
                                    }
                                    File.WriteAllBytes(dstName, zipdata);
                                }
                                else
                                {
                                    Logger.Print(string.Format("\t- Unpack {0}", vitem.FileName));
                                    byte[] zipdata = lbPackage.GetRaw(vitem.FileName);
                                    string dstName = Path.Combine(dirname, vitem.FileName);

                                    byte[] dezipdata = lbPackage.Unpack(vitem.FileName);

                                    File.WriteAllBytes(dstName + ".decdata", dezipdata);

                                    vSubItems[p].NeedReCompress = false;
                                    File.WriteAllBytes(dstName, zipdata);
                                }
                            }
                        }
                        else
                        {

                        }
                        table.Files.Add(new SubFile()
                        {
                            FileName = vEntry.FullName,
                            SubItems = vSubItems
                        });
                    }
                }
            }

            string jsontable = JsonHelper.Serialize(table);
            File.WriteAllText("dds3_table.json",jsontable,new UTF8Encoding(false));
        }

        public class Entry
        {
            public int Offset;
            public int Size;
            public string FullName;
            public int Ptr;
        }
    }

    public class DDTFileTable
    {
        public List<SubFile> Files = new List<SubFile>();
    }

    public class SubFile
    {
        public string FileName;
        public List<SubItem> SubItems = new List<SubItem>();
    }

    public class SubItem
    {
        public string FileName = "";
        public int FileID = 0;
        public uint ExtMagic = 0;
        public bool IsCompressed = false;
        public bool NeedReCompress = false;
    }


}
