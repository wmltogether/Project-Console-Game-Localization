using System;
using System.Collections.Generic;
using System.IO;

namespace DecryptSetsuna
{
    class Program
    {
        private static void DecryptFile(string target_name, string dest_name)
        {
            Console.WriteLine(target_name);
            string base_name = Path.GetFileName(target_name);
            FileStream fs = new FileStream(target_name, FileMode.Open);
            long size = fs.Length;
            byte[] src = new byte[size];
            fs.Read(src, 0, src.Length);
            fs.Close();
            byte[] dst = ParameterManager.DecryptParameter(src);
            FileStream ds = new FileStream(dest_name, FileMode.Create);
            ds.Write(dst, 0, dst.Length);
            ds.Close();

        }

        private static void EncryptFile(string target_name, string dest_name)
        {
            Console.WriteLine(target_name);
            string base_name = Path.GetFileName(target_name);
            FileStream fs = new FileStream(target_name, FileMode.Open);
            long size = fs.Length;
            byte[] src = new byte[size];
            fs.Read(src, 0, src.Length);
            fs.Close();
            byte[] dst = ParameterManager.EncryptParameter(src);
            FileStream ds = new FileStream(dest_name, FileMode.Create);
            ds.Write(dst, 0, dst.Length);
            ds.Close();

        }


        static void Main(string[] args)
        {
            string inFile = "";
            string outFile = "";
            bool doDecrypt = false;
            bool doEncrypt = false;

            if (args.Length == 0)
            {
                Console.WriteLine("err:no args given");
                Console.WriteLine("-d decrypt setsuna paraments");

                Console.WriteLine("-i input file name");
                Console.WriteLine("-o output file name");
                return;
            }
            for (int i = 0; i < args.Length; i++)
            {
                string option = args[i];
                if (option[0] == '-')
                {
                    switch (option[1])
                    {
                        case 'i':
                            inFile = args[i + 1];
                            break;
                        case 'o':
                            outFile = args[i + 1];
                            break;
                        case 'd':
                            doDecrypt = true;
                            break;
                        case 'c':
                            doEncrypt = true;
                            break;
                        default:
                            break;

                    }
                }
            }
            if (inFile == "")
            {
                Console.WriteLine("ERROR :You must give -i argv");
                return;
            }

            if (!File.Exists(inFile))
            {
                Console.WriteLine("ERROR :INPUT FILE NOT EXISTS");
                return;
            }
            if (doDecrypt)
            {
                DecryptFile(inFile, outFile);
            }


        }
    }
}


