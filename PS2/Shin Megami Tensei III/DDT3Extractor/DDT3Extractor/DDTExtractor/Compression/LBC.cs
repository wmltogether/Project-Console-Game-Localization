using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Runtime.InteropServices;
using AtlusGames.Extension;

namespace AtlusGames.Compression
{

    public class LBCPythonWrapper
    {
        public static byte[] LB_Decompress(byte[] input, int decompressLength)
        {
            byte[] result;
            LBC.Decompress(input, input.Length,decompressLength,out result);
            return result;
        }

        public static byte[] LB_Compress(byte[] input)
        {
            byte[] result;
            int resultLength;
            LBC.Compress(input, out result,out resultLength);
            return result;
        }

    }
    public class LBC
    {
        public static void Compress(byte[] inputData, out byte[] dstBytes, out int compressLength)
        {
            compressLength = 0;
            dstBytes = new byte[0];
            //这个方法很污,完全不压缩数据，很容易出问题，不要模仿
            int MAX_WND = 0x10;
            MemoryStream inputStream = new MemoryStream(inputData);
            BinaryReader br = new BinaryReader(inputStream);
            br.BaseStream.Seek(0, SeekOrigin.Begin);
            using (MemoryStream ms = new MemoryStream())
            {
                using (BinaryWriter bw = new BinaryWriter(ms))
                {
                    
                    int vLen = inputData.Length;
                    int vCounts = 0;
                    if (vLen % MAX_WND == 0)
                    {
                        vCounts = vLen / MAX_WND;
                    }
                    else
                    {
                        vCounts = vLen / MAX_WND +　1;
                    }
                    BitIO.BitWrite bitWrite = new BitIO.BitWrite(bw);
                    byte[] tmp = new byte[MAX_WND];
                    for (int i = 0; i < vCounts; i++)
                    {
                        tmp = br.ReadBytes(MAX_WND);
                        bw.Write((byte)0);
                        bw.Write((ushort)tmp.Length);
                        bw.Write(tmp);
                    }
                    bw.Write((byte)0xff);
                }
                dstBytes = ms.ToArray();
                compressLength = dstBytes.Length;
            }

        }

        public static void Decompress(byte[] data, int compressLength, int decompressLength, out byte[] dstBytes)
        {
            dstBytes = new byte[decompressLength];
            int comPos = 0; //压缩位置
            int decomPos = 0;//解压位置
            int flag = 0;//压缩标记
            int off = 0;
            int retLength = 0;
            int retOff = 0;
            byte[] wnd = new byte[0];
            byte tmp = (byte)0;
            using (MemoryStream ms = new MemoryStream(data))
            {
                using (BinaryReader br = new BinaryReader(ms))
                {
                    BitIO.BitReader bitReader = new BitIO.BitReader(br);
                    while (decomPos < decompressLength)
                    {
                        comPos = (int)br.BaseStream.Position;
                        flag = bitReader.ReadBits(3);
                        off = bitReader.ReadBits(5);
                        //Console.WriteLine(String.Format("flag:{0:x8},off:{1:x8},at offset:{2:x8},decoffset:{3:x8}", flag,off, comPos, decomPos));
                        if (flag == 0)
                        {
                            //如果前三个bit 0 0 0，不压缩，原样输出后面的off字节到解压流
                            if (off == 0)
                            {
                                off = br.ReadInt16();
                            }
                            wnd = br.ReadBytes(off);
                            Buffer.BlockCopy(wnd, 0, dstBytes, decomPos, off);
                            decomPos += off;
                        }
                        else if (flag == 1)
                        {
                            tmp = 0;
                            //如果前三个bit是0 0 1 ，压缩，默认填充0，让解压流向后填充off字节
                            if (off == 0)
                            {
                                off = br.ReadInt16();
                            }

                            if (off == -1)
                            {
                                off = br.ReadByte() * 0x100;
                            }
                            wnd = Enumerable.Repeat((byte)0, off).ToArray();
                            Buffer.BlockCopy(wnd, 0, dstBytes, decomPos, off);
                            decomPos += off;
                        }
                        else if (flag == 2)
                        {
                            if (off == 0)
                            {
                                off = br.ReadInt16();
                            }
                            //如果前三个bit是0 1 0，压缩，复制输出后面的1字节当作填充，让解压流向后填充off字节
                            tmp = br.ReadByte();
                            wnd = Enumerable.Repeat((byte)tmp, off).ToArray();
                            Buffer.BlockCopy(wnd, 0, dstBytes, decomPos, off);
                            decomPos += off;
                        }
                        else if (flag == 3)
                        {
                            //如果前三个bit是0 1 1 压缩，回退并复制之前的内容
                            if (off == 0)
                            {
                                //如果后5位是0, 则向下读3字节
                                retLength = br.ReadInt16();//向后复制量
                                retOff = br.ReadByte();//回退读取量
                            }
                            else
                            {
                                retLength = off;//向后复制量
                                retOff = br.ReadByte();//回退读取量
                            }
                            wnd = new byte[retOff];
                            Buffer.BlockCopy(dstBytes, decomPos - retOff, wnd, 0, retOff);//从dstBytes复制之前的内容到临时的wnd
                            int kL = 0;
                            int kO = 0;
                            while (kL < retLength)
                            {
                                dstBytes[decomPos + kL] = wnd[kO];
                                kO += 1;
                                kL += 1;
                                if (kO >= retOff) kO = 0;
                            }
                            decomPos += retLength;
                        }
                        else if (flag == 4)
                        {
                            //如果前三个bit是1 0 0 压缩，让压缩流回退retOff字节，并复制之前的内容（复制retLength个字节）
                            if (off == 0)
                            {
                                //如果后5位是0, 则向下读4字节
                                retLength = br.ReadInt16();//向后复制量
                                retOff = br.ReadInt16();
                            }
                            else
                            {
                                retLength = off;//向后复制量
                                retOff = br.ReadInt16();//回退读取量
                            }
                            wnd = new byte[retOff];
                            Buffer.BlockCopy(dstBytes, decomPos - retOff, wnd, 0, retOff);//从dstBytes复制之前的内容到临时的wnd
                            int kL = 0;
                            int kO = 0;
                            while (kL < retLength)
                            {
                                dstBytes[decomPos + kL] = wnd[kO];
                                kO += 1;
                                kL += 1;
                                if (kO >= retOff) kO = 0;
                            }
                            decomPos += retLength;

                        }
                        else if (flag == 5)
                        {
                            //扩展补位，1字节变2字节
                            int extLen = off;
                            if (off == 0)
                            {
                                extLen = br.ReadInt16();
                            }
                            //如果前三个bit是1 0 1 ，让压缩流往下读off字节，每个字节从8bit扩展到16bit，写入到解压流
                            for (int i = 0; i < extLen * 2; i+=2)
                            {
                                tmp = br.ReadByte();
                                dstBytes[decomPos + i] = tmp;
                            }
                            decomPos += (extLen * 2);

                        }
                        else if (flag == 6)
                        {
                            //???怎么还有6
                            Console.WriteLine(String.Format("unk flag:{0:x8},at offset:{1:x8},decompress::{2:x8}", flag, comPos, decomPos));
                        }
                        else if (flag == 7)
                        {
                            //如果前三个bit是1 1 1break，停止解压操作
                            break;
                        }
                        else
                        {
                            Console.WriteLine(String.Format("unk flag:{0:x8},at offset:{1:x8},decompress::{2:x8}", flag, comPos, decomPos));
                        }
                    }
                }
            }
        }
    }
}
