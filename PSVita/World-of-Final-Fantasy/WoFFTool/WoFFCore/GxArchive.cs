using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.IO.Compression;
using Core.IO;



namespace WoFFCore
{

    public class GxArchive
    {
        public uint Magic;
        public byte[] index_data;
        public List<uint> gdat_index;

        public GxArchive(string filename ,string tablename)
        {
            using (EndianBinaryReader br = new EndianBinaryReader(File.Open(tablename, FileMode.Open), Endian.BigEndian))
            {
                Magic = br.ReadUInt32();
                if (Magic != 0x00687363)// \0hsc
                {
                    throw new Exception("csh table Magic Error");
                }
                br.BaseStream.Seek(0x80, SeekOrigin.Begin);
                BILZ bilz = new BILZ(br.BaseStream);
                index_data = bilz.index_data;
            }
            using (EndianBinaryReader br = new EndianBinaryReader(File.Open(filename, FileMode.Open), Endian.LittleEndian))
            {
                Magic = br.ReadUInt32();
                gdat_index = new List<uint>();
                if (Magic != 0x54414447)// \0hsc
                {
                    throw new Exception("GDAT Magic Error");
                }
                int nums = br.ReadInt32();
                for (int i = 0; i < nums; i++)
                {
                    br.BaseStream.Seek(0x8 + 0x8 * i,SeekOrigin.Begin);
                    uint offset = br.ReadUInt32();
                    uint size = br.ReadUInt32();
                    gdat_index.Add(offset);
                    Console.WriteLine("Got GDAT {0:x8}", (int)offset);
                }
            }

        }
        
    }

    public class BILZ
    {
        public byte[] index_data;
        public BILZ(Stream stream, int pos = 0)
        {
            EndianBinaryReader br = new EndianBinaryReader(stream, Endian.BigEndian);
            br.BaseStream.Seek(pos,SeekOrigin.Begin);
            if (br.ReadUInt32() == 0x42494c5a)
            {
                uint dec_size = br.ReadUInt32();
                uint enc_size = br.ReadUInt32();
                uint com_type = br.ReadUInt32();
                byte[] enc_data = br.ReadBytes((int)enc_size);
                Zlib.Decomress(enc_data, out index_data);

            }


        }
    }
}
