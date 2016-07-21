using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace t3bpkg
{

    class Program
    {
        #region show help message
        static void ShowHelp()
        {
            
            Console.WriteLine("Usage:");
            Console.WriteLine(" -x - Extract all files.");
            Console.WriteLine(" -r - Reimport all files.");
            Console.WriteLine(" -o OUT_FILE - Set output file.");
            Console.WriteLine(" -d OUT_DIR - Set output directory.");
            Console.WriteLine(" -i IN_FILE - Set input file.");
            Console.WriteLine(" -f IN_FOLDER - Set import folder.");
            Console.WriteLine(" -h HELP");
            Console.WriteLine("[Extract]t3bpkg.exe -x -i 3rd.fsd -d 3rd.pkg_unpacked"); 
            Console.WriteLine("[import]t3bpkg.exe -r -i 3rd.fsd -f 3rd.pkg_unpacked -d import");
        }
        #endregion
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("error: no args\n");
                Console.WriteLine("====================");
                ShowHelp();
                return;
            }
            bool doExtract = false;
            bool doReimport = false;
            string outDir = ".";
            string inFile = "";
            string outFile = "";

            string inFolder = "./";
            string inTableTxt = "FSD_INFO.txt";
            for (int i = 0; i < args.Length; i++)
            {
                string option = args[i];
                if (option[0] == '-')
                {
                    switch (option[1])
                    {
                        case 'x': doExtract = true; break;
                        case 'r': doReimport = true; break;
                        case 'd': outDir = args[i + 1]; break;
                        case 'i': inFile = args[i + 1]; break;
                        case 'f': inFolder = args[i + 1]; break;
                        case 'o': outFile = args[i + 1]; break;       
                        case 'h': ShowHelp(); break;
                        default: ShowHelp(); break;
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

            if (!(doExtract || doReimport))
            { //Lazy sanity checking for now
                Console.WriteLine("no? \n");
                return;
            }
            if (doExtract)
            #region doExtract
            {
                string fsd_name = inFile;
                if (fsd_name.Contains(".pkg"))
                {
                    fsd_name = fsd_name.Replace(".pkg", ".fsd");
                }
                string pkg_name = fsd_name.Replace(".fsd", ".pkg");
                byte[] fsdData = File.ReadAllBytes(fsd_name);
                LBA lba = new LBA();
                lba.GetLBA(fsdData);
                BinaryReader pkg_reader = new BinaryReader(File.Open(pkg_name, FileMode.Open));

                if (!Directory.Exists(outDir))
                {
                    Directory.CreateDirectory(outDir);
                }

                FileStream info = new FileStream("FSD_INFO.txt", FileMode.Create);
                StreamWriter sw = new StreamWriter(info);
                foreach (var item in lba.LBATable)
                {
                    int _cnt_id = item.LBA_ID;
                    uint _cnt_offset = item.LBA_OFFSET;
                    uint _cnt_size = item.LBA_SIZE;
                    pkg_reader.BaseStream.Seek(_cnt_offset, SeekOrigin.Begin);
                    byte[] data = pkg_reader.ReadBytes((int)_cnt_size);

                    if (_cnt_size > 0)
                    {
                        byte[] hdr = new byte[8];
                        Array.Copy(data, 0, hdr, 0, 8);
                        FileType ftype = new FileType(hdr);
                        if (_cnt_id == 16)
                        {
                            ftype.ext_name = ".font";
                        }
                        if (_cnt_id == 19)
                        {
                            ftype.ext_name = ".lang";
                        }
                        Console.WriteLine(String.Format("{0:d8}{1},{2:x8},{3:x8}\n", _cnt_id, ftype.ext_name, _cnt_offset, _cnt_size));
                        File.WriteAllBytes(outDir + "/" + String.Format("{0:d8}{1}", _cnt_id, ftype.ext_name), data);
                        sw.Write(String.Format("{0:d8}{1},{2:x8},{3:x8}\r\n", _cnt_id, ftype.ext_name, _cnt_offset, _cnt_size));
                    }
                    else
                    {
                        Console.WriteLine(String.Format("{0:d8},{1:x8},{2:x8}\n", _cnt_id, _cnt_offset, _cnt_size));
                        sw.Write(String.Format("{0:d8}.null,{1:x8},{2:x8}\r\n", _cnt_id, _cnt_offset, _cnt_size));
                    }

                }
                sw.Close();
                info.Close();
                pkg_reader.Close();
            }
            #endregion
            if (doReimport)
            #region doReimport
            //
            {
                if (!Directory.Exists(outDir))
                {
                    Directory.CreateDirectory(outDir);
                }
                string fsd_name = inFile;
                if (fsd_name.Contains(".pkg"))
                {
                    fsd_name = fsd_name.Replace(".pkg", ".fsd");
                }
                string pkg_name = fsd_name.Replace(".fsd", ".pkg");
                BinaryWriter pkg_writer = new BinaryWriter(File.Create(String.Format("{0}/3rd.pkg" , outDir)));
                LBA lba = new LBA();
                lba.SetLBA(inTableTxt, inFile, inFolder, pkg_writer);
                pkg_writer.Close();
                MemoryStream fsd_stream = new MemoryStream(File.ReadAllBytes(inFile));
                BinaryWriter fsd_writer = new BinaryWriter(fsd_stream);
                fsd_writer.Seek(0x18, SeekOrigin.Begin);
                fsd_writer.Write((uint)lba.fsdHeader.pkg_size);
                fsd_writer.Seek((int)lba.fsdHeader.start_offset, SeekOrigin.Begin);
                for (int i = 0; i < lba.LBATable.Count; i++)
                {
                    if ((lba.LBATable[i].LBA_SIZE > 0) && lba.LBATable[i].LBA_SIZE % 0x800 != 0)
                    {
                        uint temp = lba.LBATable[i].LBA_OFFSET / 0x800 +
                                ((lba.LBATable[i].LBA_SIZE % 0x800) << 20);
                        fsd_writer.Write(temp);
                    }
                    else if (lba.LBATable[i].LBA_SIZE == 0)
                    {
                        uint temp = lba.LBATable[i].LBA_OFFSET / 0x800 +
                                ((uint)0x0 << 20);
                        fsd_writer.Write(temp);
                    }
                    else
                    {
                        uint temp = lba.LBATable[i].LBA_OFFSET / 0x800 +
                                ((uint)0x800 << 20);
                        fsd_writer.Write(temp);
                    }
                    fsd_writer.Write((uint)1);
                }
                fsd_writer.Write(lba.fsdHeader.pkg_size / 0x800);
                fsd_writer.Write((uint)1);
                fsd_writer.Close();
                using (BinaryWriter br = new BinaryWriter(File.Create(String.Format("{0}/3rd.fsd", outDir))))
                {
                    br.Write(fsd_stream.ToArray());
                }
                fsd_stream.Close();
                pkg_writer.Close();


            }
            #endregion
        }
    }
}
