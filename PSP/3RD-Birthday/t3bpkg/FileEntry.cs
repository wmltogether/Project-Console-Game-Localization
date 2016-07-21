using System;
using System.Collections.Generic;
using System.Text;
using System.IO;

namespace t3bpkg
{
    public enum DataType
    {
        None,
        PNG,
        PMF,
        LANG,
        GIM,
        AUDIO,
        PACK,
    }
    

    class FileType
    {
        public string ext_name = ".bin";
        private Dictionary<uint, DataType> _fTypeDict = new Dictionary<uint, DataType>{
                                                            {0x6b636170,DataType.PACK},
                                                            {0x42444553,DataType.AUDIO},
                                                            {0x474E5089,DataType.PNG},
                                                            {0x464D5350,DataType.PMF},
                                                      };
        public FileType(byte[] data)
        {

            MemoryStream ms = new MemoryStream(data);
            BinaryReader br = new BinaryReader(ms);
            uint key = br.ReadUInt32();
            if (_fTypeDict.ContainsKey(key))
            {
                switch (_fTypeDict[key])
                {
                    case DataType.PACK: ext_name = ".pack"; break;
                    case DataType.AUDIO: ext_name = ".at3"; break;
                    case DataType.PNG: ext_name = ".png"; break;
                    case DataType.PMF: ext_name = ".pmf"; break;
                    case DataType.LANG: ext_name = ".lang"; break;
                    case DataType.GIM: ext_name = ".gim"; break;
                    default: ext_name = ".bin"; break;
                }
            }
            ms.Close();
            br.Close();
        }


    }
}
