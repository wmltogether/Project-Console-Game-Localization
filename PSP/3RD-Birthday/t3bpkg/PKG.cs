using System;
using System.Collections.Generic;
using System.Text;
using System.IO;

namespace t3bpkg
{
    public class PKG
    {
        
        public LBA lba;
    }
    public class FSDHeader
    {
        public int nums;
        public uint start_offset;
        public uint end_offset;
        public uint pkg_size;

        public FSDHeader(MemoryStream ms)
        {
            BinaryReader br = new BinaryReader(ms);
            br.BaseStream.Seek((long)0x8, SeekOrigin.Begin);
            nums = br.ReadInt32();
            br.BaseStream.Seek((long)0x4, SeekOrigin.Current);
            start_offset = br.ReadUInt32();
            end_offset = br.ReadUInt32();
            pkg_size = br.ReadUInt32();

        }
    }
    public class FileEntry
    {
        public uint LBA_OFFSET;
        public uint LBA_SIZE;
        public int LBA_ID;
        public string NAME;

    }

    public class LBA
    {
        public FSDHeader fsdHeader;

        public List<FileEntry> LBATable;

        public void SetLBA(string inTableTxt , string inFile, string inFolder ,BinaryWriter pkg_writer)
        {
            LBATable = new List<FileEntry>();
            string[] table = File.ReadAllLines(inTableTxt, System.Text.Encoding.UTF8);
            uint lines = (uint)table.Length;
            uint _current_offset = 0;
            #region READ TABLE
            if (lines > 1)
            {
                
                for (int f = 0; f < lines; f++)
                {
                    string _current_line = table[f];
                    if (_current_line.Contains(","))
                    {
                        _current_line = _current_line.Replace("\r", "");
                        _current_line = _current_line.Replace("\n", "");
                        string[] items = _current_line.Split(',');
                        string _name = items[0];
                        FileEntry fileEntry = new FileEntry();
                        if (_name.Contains(".null"))
                        {
                            fileEntry.LBA_OFFSET = (uint)_current_offset;
                            fileEntry.LBA_SIZE = (uint)0;
                            fileEntry.LBA_ID = f;
                            LBATable.Add(fileEntry);
                        }
                        else
                        {

                            //FileInfo fileInfo = new FileInfo(String.Format("{0}/{1}" , inFolder , _name));
                            Console.WriteLine(String.Format("Reading : {0}/{1}", inFolder, _name));
                            byte[] _current_data = File.ReadAllBytes(String.Format("{0}/{1}", inFolder, _name));
                            uint _current_length = (uint)_current_data.Length;
                            uint mod = _current_length % 0x800;
                            fileEntry.LBA_OFFSET = (uint)pkg_writer.BaseStream.Position;
                            fileEntry.LBA_SIZE = (uint)_current_length;
                            fileEntry.LBA_ID = f;
                            fileEntry.NAME = String.Format("{0}/{1}", inFolder, _name);
                            LBATable.Add(fileEntry);
                            pkg_writer.Write(_current_data);
                            if (mod != 0)
                            {
                                pkg_writer.Write(new byte[0x800 - mod]);
                            }
                            _current_offset = (uint)pkg_writer.BaseStream.Position;
                        }   
                    }
                }
            }
            #endregion
            fsdHeader = new FSDHeader(new MemoryStream(File.ReadAllBytes(inFile)));
            fsdHeader.pkg_size = _current_offset;

        }
        public void GetLBA(byte[] Data)
        {
            MemoryStream ms = new MemoryStream(Data);
            fsdHeader = new FSDHeader(ms);
            BinaryReader br = new BinaryReader(ms);
            LBATable = new List<FileEntry>();
            br.BaseStream.Seek(fsdHeader.start_offset , SeekOrigin.Begin);
            for (int i = 0; i < fsdHeader.nums; i++)
            {
                br.BaseStream.Seek(fsdHeader.start_offset + i * 8, SeekOrigin.Begin);
                uint t0 = br.ReadUInt32();
                uint t1 = br.ReadUInt32();
                FileEntry fe = new FileEntry();
                fe.LBA_ID = i;
                if (fsdHeader.start_offset + i * 8 + 8 < fsdHeader.end_offset)
                {
                    uint t2 = br.ReadUInt32();
                    fe.LBA_OFFSET = (t0 & 0x0fffff) * 0x800;
                    uint mod = (uint)((uint)t0 >> 20);
                    if ((t2 & 0x0fffff) == (t0 & 0x0fffff))
                    {
                        fe.LBA_SIZE = mod;
                    }
                    else
                    {
                       
                        fe.LBA_SIZE = (((t2 - t0 - 1) & 0x0fffff) * 0x800) + mod;               
                    }    
                }
                else
                {
                    fe.LBA_OFFSET = (t0 & 0x0fffff) * 0x800;
                    uint mod = (t0 >> 20);
                    fe.LBA_SIZE = fsdHeader.pkg_size - (((t0 - 1) & 0x0fffff) * 0x800) + mod;
                }
                if (fe.LBA_OFFSET < 0)
                {
                    throw new Exception(String.Format("{0:x8} Error LBA < 0", fsdHeader.start_offset + i * 8));
                }
                LBATable.Add(fe);
                
                
 
            }
            br.Close();
            ms.Close();
        }

    }
}
