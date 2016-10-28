using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using ICSharpCode.SharpZipLib.Zip.Compression;
using ICSharpCode.SharpZipLib.Zip.Compression.Streams;

namespace WoFFCore
{
    public static class Zlib
    {
        public static void Decomress(byte[] input, out byte[] output)
        {
            using (MemoryStream fs = new MemoryStream(input))
            {
                using (InflaterInputStream ds = new InflaterInputStream(fs))
                {

                    MemoryStream fso = new MemoryStream();
                    fso.Seek(0, SeekOrigin.Begin);
                    byte[] data = new byte[256];
                    while (true)
                    {
                        int rs = ds.Read(data, 0, data.Length);
                        fso.Write(data, 0, rs);
                        if (rs == 0) break;
                    }
                    output = fso.ToArray();
                    fso.Close();
                }
            }
        }
    }
}
