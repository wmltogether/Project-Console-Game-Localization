using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace AtlusGames.Extension
{
    public static class BinaryExtension
    {
        private static Encoding ENCODING_SHIFT_JIS = Encoding.GetEncoding("Shift_JIS");
        public static void AlignPosition(this BinaryReader reader, int alignmentBytes)
        {
            reader.BaseStream.Position = Align(reader.BaseStream.Position, alignmentBytes);
        }

        public static void AlignPosition(this BinaryWriter writer, int alignmentBytes)
        {
            long align = Align(writer.BaseStream.Position, alignmentBytes);
            writer.Write(new byte[(align - writer.BaseStream.Position)]);
        }

        public static string ReadCString(this BinaryReader reader)
        {
            List<byte> bytes = new List<byte>();
            byte b = reader.ReadByte();
            while (b != 0)
            {
                bytes.Add(b);
                b = reader.ReadByte();
            }
            return ENCODING_SHIFT_JIS.GetString(bytes.ToArray());
        }

        internal static long Align(long value, int alignment)
        {
            return (value + (alignment - 1)) & ~(alignment - 1);
        }

        internal static int Align(int value, int alignment)
        {
            return (value + (alignment - 1)) & ~(alignment - 1);
        }

    }
}
