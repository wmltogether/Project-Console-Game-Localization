using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using AtlusGames.Compression;
using AtlusGames.GameFormat;

namespace DDTExtractor
{
    class Program
    {
        static void Main(string[] args)
        {
            if (!Directory.Exists("UNPACK/"))
            {
                Directory.CreateDirectory("UNPACK/");
            }
            if (!Directory.Exists("PATCH/"))
            {
                Directory.CreateDirectory("PATCH/");
            }
            if (!Directory.Exists("IMPORT/"))
            {
                Directory.CreateDirectory("IMPORT/");
            }



            Console.Clear();
            Console.WriteLine("选择执行模式");
            Console.WriteLine("\t 按1 解包");
            Console.WriteLine("\t 按2 打包");
            Console.WriteLine("\t 按esc 退出");
            ConsoleKeyInfo info = Console.ReadKey();
            switch (info.Key)
            {
                case ConsoleKey.D1:
                    DDT ddtContainer = new DDT("./dds3.img", "./dds3.ddt");
                    ddtContainer.GetEntry();
                    ddtContainer.Extract("UNPACK");
                    Console.WriteLine("解包完毕");
                    Console.ReadLine();
                    break;
                case ConsoleKey.D2:
                    DDT ddtContainers = new DDT("./dds3.img", "./dds3.ddt");
                    ddtContainers.Repack("./UNPACK/", "./PATCH/", "./IMPORT/");
                    Console.WriteLine("打包完毕");
                    Console.ReadLine();
                    break;
                case ConsoleKey.Escape:
                    Environment.Exit(0);
                    break;

            }





            //test();
            //Console.WriteLine("alldone, have fun");

        }

        static void test()
        {
            using (FileStream fs = File.OpenRead("test.LB"))
            {
                int length = 0x269a - 0x10;
                int decLen = 0x501e;
                int offset = 0x4d0;
                byte[] dataBytes = new byte[length];
                BinaryReader br = new BinaryReader(fs);
                br.BaseStream.Seek(offset, SeekOrigin.Begin);
                dataBytes = br.ReadBytes(length);
                byte[] outBytes = new byte[decLen];
                LBC.Decompress(dataBytes,length, decLen,out outBytes);
                File.WriteAllBytes("test.dec", outBytes);
            }
        }
    }
}
