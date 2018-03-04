using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using AtlusGames.Compression;
using AtlusGames.Extension;


namespace AtlusGames.GameFormat
{
    public class LB:IDisposable
    {
        public const int ALIGNMENT_SIZE = 0x40;
        public List<SubItem> SubItems = new List<SubItem>();
        private Dictionary<string, int> posDictionary = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
        private MemoryStream ms;
        private int packageSize = 0;
        private string baseName;
        public LB()
        {

        }

        public void Load(string path)
        {
            baseName = Path.GetFileNameWithoutExtension(path);
            byte[] data = File.ReadAllBytes(path);
            ms = new MemoryStream(data);
            ms.Seek(0, SeekOrigin.Begin);
            packageSize = data.Length;
            GetEntry();


        }

        public void GetEntry()
        {
            SubItems = new List<SubItem>();
            int pos = 0;
            ms.Seek(0, SeekOrigin.Begin);
            BinaryReader br = new BinaryReader(ms);
            int nid = 0;
            while (pos < packageSize - 0x40)
            {
                br.BaseStream.Seek(pos, SeekOrigin.Begin);
                int sig = br.ReadInt32();
                if (((sig & 0xffff ) == 0x101))//压缩了
                {
                    br.BaseStream.Seek(-4, SeekOrigin.Current);
                    int ptr = (int)br.BaseStream.Position;
                    int filehdr = br.ReadInt32();
                    int compressSize = br.ReadInt32();
                    uint fileType = br.ReadUInt32();
                    int decompressSize = br.ReadInt32();
                    string fName = string.Format("{0}_LB_{1}.{2}", this.baseName, nid, GetFileExtension(fileType));
                    SubItem subItem = new SubItem
                    {
                        FileName = fName,
                        FileID = filehdr,
                        IsCompressed = true,
                        ExtMagic = fileType,
                        NeedReCompress = false
                    };
                    posDictionary.Add(fName, ptr);
                    SubItems.Add(subItem);
                    pos += compressSize;
                    if (pos % 0x40 != 0)
                    {
                        pos += (0x40 - pos % 0x40);
                    }
                    nid += 1;
                }
                else
                {
                    //没压缩
                    br.BaseStream.Seek(-4, SeekOrigin.Current);
                    int ptr = (int)br.BaseStream.Position;
                    int filehdr = br.ReadInt32();
                    int decompressSize = br.ReadInt32();
                    uint fileType = br.ReadUInt32();
                    string fName = string.Format("{0}_{1}.{2}", this.baseName, nid, GetFileExtension(fileType));
                    SubItem subItem = new SubItem
                    {
                        FileName = fName,
                        FileID = filehdr,
                        IsCompressed = false,
                        NeedReCompress = false
                    };
                    posDictionary.Add(fName, ptr);
                    SubItems.Add(subItem);
                    pos += decompressSize;
                    if (pos % 0x40 != 0)
                    {
                        pos += (0x40 - pos % 0x40);
                    }
                    nid += 1;
                }
            }

        }

        public byte[] GetRaw(string itemName)
        {
            byte[] result = new byte[1];
            SubItem subItem;
            if (HasItem(itemName, out subItem))
            {
                int ptr = posDictionary[itemName];
                BinaryReader br = new BinaryReader(ms);
                br.BaseStream.Seek(ptr, SeekOrigin.Begin);
                if (subItem.IsCompressed)
                {
                    int filehdr = br.ReadInt32();
                    int compressSize = br.ReadInt32();
                    uint fileType = br.ReadUInt32();
                    int decompressSize = br.ReadInt32();
                    br.BaseStream.Seek(-0x10, SeekOrigin.Current);
                    result = br.ReadBytes(compressSize);
                }
                else
                {
                    int filehdr = br.ReadInt32();
                    int decompressSize = br.ReadInt32();
                    br.BaseStream.Seek(-8, SeekOrigin.Current);
                    result = br.ReadBytes(decompressSize);
                }
            }

            return result;
        }

        public byte[] Unpack(string itemName)
        {
            byte[] result = new byte[1];
            SubItem subItem;
            if (HasItem(itemName, out subItem))
            {
                int ptr = posDictionary[itemName];
                BinaryReader br = new BinaryReader(ms);
                br.BaseStream.Seek(ptr, SeekOrigin.Begin);
                Logger.Print(string.Format("{0:x8}", ptr));
                if (subItem.IsCompressed)
                {
                    int filehdr = br.ReadInt32();
                    int compressSize = br.ReadInt32();
                    uint fileType = br.ReadUInt32();
                    int decompressSize = br.ReadInt32();
                    byte[] zipdata = br.ReadBytes(compressSize - 0x10);
                    
                    LBC.Decompress(zipdata, zipdata.Length, decompressSize,out result);
                }
                else
                {
                    int filehdr = br.ReadInt32();
                    int decompressSize = br.ReadInt32();
                    br.BaseStream.Seek(-8, SeekOrigin.Current);
                    result = br.ReadBytes(decompressSize);
                }
            }

            return result;
        }

        public byte[] Repack(string baseDir, string lbName, string srcDir, string patchDir, List<SubItem> subItems)
        {
            byte[] dst;
            this.Load(IOHelper.PathCombine(srcDir, lbName));
            using (MemoryStream dstStream = new MemoryStream())
            {
                using (BinaryWriter bw = new BinaryWriter(dstStream))
                {
                    bw.Seek(0, SeekOrigin.Begin);
                    for (int i = 0; i < subItems.Count; i++)
                    {
                        SubItem vItem = subItems[i];
                        byte[] vDataBytes;
                        if (File.Exists(IOHelper.PathCombine(patchDir, baseDir, vItem.FileName)))
                        {
                            //如果存在补丁文件，从补丁目录读取并压缩数据
                            vDataBytes = File.ReadAllBytes(IOHelper.PathCombine(patchDir, baseDir, vItem.FileName));
                        }
                        else
                        {
                            //如果不存在补丁文件，从原始目录读取
                            vDataBytes = File.ReadAllBytes(IOHelper.PathCombine(srcDir, baseDir, vItem.FileName));
                        }
                        if ((vItem.NeedReCompress == true) && (vItem.IsCompressed == true))
                        {
                            byte[] compressDataBytes;
                            int compressLenght = 0;
                            LBC.Compress(vDataBytes, out compressDataBytes, out compressLenght);
                            bw.Write((int)vItem.FileID);
                            bw.Write((int)compressLenght + 0x10);
                            bw.Write((uint)vItem.ExtMagic);
                            bw.Write((int)vDataBytes.Length);
                            bw.Write(compressDataBytes);
                            bw.AlignPosition(0x40);
                        }

                        else if ((vItem.NeedReCompress == false) && (vItem.IsCompressed == true))
                        {
                            bw.Write(vDataBytes);
                            bw.AlignPosition(0x40);
                        }
                        else
                        {
                            bw.Write(vDataBytes);
                            bw.AlignPosition(0x40);
                        }
                    }
                    bw.Write((int)0xff);
                    bw.Write((int)0x10);
                    bw.Write((uint)0x30444e45);
                    bw.Write((int)0);
                    bw.Write(Enumerable.Repeat((byte)0, 0x30).ToArray());
                    dst = dstStream.ToArray();
                }

            }

            return dst;
        }

        public void Dispose()
        {
            ms?.Dispose();
        }

        public string GetFileExtension(uint ftype)
        {
            string dst = "bin";
            switch (ftype)
            {
                case 0x00004642:
                    dst = "bf";
                    break;
                case 0x00434150:
                    dst = "PAC";
                    break;
                case 0x00444D54:
                    dst = "TMD";
                    break;
                case 0x004E4254:
                    dst = "TBN";
                    break;
                case 0x4e584d54:
                    dst = "TMX";
                    break;
                case 0x30584d54:
                    dst = "TMX";
                    break;

            }

            return dst;
        }

        public bool HasItem(string name,out SubItem item)
        {
            item = null;
            foreach (var k in SubItems)
            {
                if (k.FileName.ToLower().Equals(name.ToLower()))
                {
                    item = k;
                    return true;
                }
            }

            return false;
        }
    }
}
