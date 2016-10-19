using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Dynamic;

namespace Core.IO
{
    
    public static class Struct
    {

        /// <summary>
        /// 
        /// Simple python-like Struct unpacker, quick unpack multi data structure from binary
        /// 
        /// </summary>
        /// <param name="fmt">python-like structure type</param>
        /// <param name="input">input bytes</param>
        /// <returns>dynamic structure</returns>
        public static dynamic[] Unpack(string fmt , byte[] input)
        {
            Endian endian = Endian.LittleEndian;
            EndianBinaryReader br;
            if (fmt.Length < 2)
            {
                throw new Exception("Error: Struct.Unpack no fmt given");
            }
            
            string hdr = fmt.Substring(0, 1);
            if (hdr == ">")
            {
                endian = Endian.BigEndian;
                br = new EndianBinaryReader(new MemoryStream(input), endian);
                fmt = fmt.Remove(0, 1);
            }
            else if (hdr == "<")
            {
                endian = Endian.LittleEndian;
                br = new EndianBinaryReader(new MemoryStream(input), endian);
                fmt = fmt.Remove(0, 1);
            }
            else
            {
                endian = Endian.LittleEndian;
                br = new EndianBinaryReader(new MemoryStream(input), endian);
            }
            int count = int.Parse(fmt.Substring(0, fmt.Length - 1));
            string sw = fmt.Substring(fmt.Length - 1, 1);
            
            if (count == 0)
            {
                throw new Exception("Error: Struct.Unpack unpack count cannot be zero");
            }
            dynamic[] output = new dynamic[count]; ;
            switch (sw)
            {
                case "B":
                    
                    for (int i = 0; i < count; i++)
                    {
                        output[i] = (uint)br.ReadByte();
                    }
                    break;
                case "b":
                    for (int i = 0; i < count; i++)
                    {
                        output[i] = (int)br.ReadSByte();
                    }
                    break;
                case "H":
                    for (int i = 0; i < count; i++)
                    {
                        output[i] = br.ReadUInt16();
                    }
                    break;
                case "h":
                    for (int i = 0; i < count; i++)
                    {
                        output[i] = (int)br.ReadInt16();
                    }
                    break;
                case "I":
                    for (int i = 0; i < count; i++)
                    {
                        output[i] = br.ReadUInt32();
                    }
                    break;
                case "i":
                    for (int i = 0; i < count; i++)
                    {
                        output[i] = (int)br.ReadInt32();
                    }
                    break;
                case "Q":
                    for (int i = 0; i < count; i++)
                    {
                        output[i] = br.ReadUInt64();
                    }
                    break;
                case "q":
                    for (int i = 0; i < count; i++)
                    {
                        output[i] = br.ReadInt64();
                    }
                    break;
                case "f":
                    for (int i = 0; i < count; i++)
                    {
                        output[i] = br.ReadSingle();
                    }
                    break;
                default:
                    throw new Exception("Error: Struct.Unpack wrong fmt given");
            }
            br.Close();
            return output;
        }
    }
}
