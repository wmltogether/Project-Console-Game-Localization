using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Core.IO
{
    public static class IOMath
    {
        /// <summary>
        /// quick swap single-byte endian
        /// 01  -> 10
        /// FE  -> EF
        /// </summary>
        /// <param name="input"></param>
        /// <returns></returns>
        public static byte Swap4byte(byte input)
        {
            byte output;
            output = (byte)(((input & 0x0F) << 4) | ((input & 0xF0) >> 4));
            return output;
        }
    }
}
