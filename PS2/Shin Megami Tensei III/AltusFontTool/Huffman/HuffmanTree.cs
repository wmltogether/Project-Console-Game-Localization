using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace Huffman
{
    public class HuffmanTree
    {
        public void Compress(byte[] Bin , string font_path)
        {
            long[,] Tree = new long[513, 8];
            string[] HS = new string[256];
            string st, t, t1;
            long i, j, k, n;
            long tn = 1;
            long node, fl, fn, nbit, bit;
            int c;
            byte b, b1;
            long addr0, addr1, addr2, addr3, addr4, addr5, addr6, addr;
            Huffman(ref Bin, ref Tree, ref tn);
            node = tn * 2 - 3;
            addr0 = 0x20;
            addr1 = (node + 1) * 6;
            addr3 = Bin.GetUpperBound(0) + 1;
            fl = 0x200;
            fn = addr3 / fl + 1;
            addr4 = fn * 4;
            addr6 = (fn - 1) * 2;
            if ((addr6 & 3) == 2)
            {
                addr6 = addr6 + 2;
            }
            addr5 = 0x64 + fn * 4 + addr6;
            using (MemoryStream ms = new MemoryStream(File.ReadAllBytes(font_path)))
            {
                using (BinaryWriter bw = new BinaryWriter(ms))
                {
                    bw.BaseStream.Seek(0 , SeekOrigin.Begin);
                    bw.BaseStream.Seek(addr5 , SeekOrigin.Begin);
                    bw.Write((Int32)addr0);
                    bw.BaseStream.Seek(addr5 + 0x10, SeekOrigin.Begin);
                    bw.Write((Int32)fl);
                    bw.Write((Int32)fn);
                    bw.Write((Int32)addr4);
                    bw.Write((Int32)addr3);
                    c = (int)node;
                    bw.Write((Int32)c);
                    c = (int)Tree[Tree[node, 7], 5];
                    bw.Write((Int32)c);
                    c = (int)Tree[Tree[node, 7], 6];
                    bw.Write((Int32)c);

                    for (i = 1; i <= node; i++)
                    {
                        c = (int)i;
                        j = Tree[i, 7];
                        if (Tree[j, 1] > 0)
                        {
                            c = 0;
                            bw.Write((Int32)c);
                            c = (int)Tree[j, 1] - 1;
                            bw.Write((Int32)c);
                        }
                        else
                        {
                            c = (int)Tree[j, 5];
                            bw.Write((Int32)c);
                            c = (int)Tree[j, 6];
                            bw.Write((Int32)c);
                        }
                    }



                }
            }


        }
        private void Huffman(ref byte[] A , ref long[,] Tree , ref long tn)
        {
            long An, Bn;
            long[] code = new long[256];
            long i, j, k, n, tm;
            long p;
            for (i = 0; i <= A.GetUpperBound(0); i++)
            {
                code[A[i]] = code[A[i]] + 1;
            }
            tn = 1;
            for (i = 0 ; i <= 255 ; i++)
            {
                if (code[i] > 0)
                {
                    for (j = i; j < tn; j++)
                    {
                        if (Tree[i, 0] > code[i])
                        {
                            break;
                        }
                    }
                    if (j < tn)
                    {
                        for (k = tn - 1; k >= j; k--)
                        {
                            Tree[k + 1, 0] = Tree[k, 0];
                            Tree[k + 1, 1] = Tree[k, 1];
                        }
                    }
                    Tree[j, 0] = code[i];
                    Tree[j, 1] = i + 1;
                    tn += 1;
                }
            }
            for (i = 1; i < tn; i++)
            {
                Tree[i, 2] = 0;
                Tree[i, 3] = 0;
                Tree[i, 5] = 0;
                Tree[i, 6] = 0;
                Tree[i, 4] = i;
                Tree[i, 7] = i;
            }
            tm = tn;
            i = 1;
            while (i < tm - 2)
            {
                n = Tree[i, 0] + Tree[i + 1, 0];
                for (j = i + 2; j <= tm - 1; j++)
                {
                    if (Tree[j, 0] >= n)
                    {
                        break;
                    }

                }
                Tree[i, 2] = tm;
                Tree[i, 3] = 1;
                Tree[i + 1, 2] = tm;
                Tree[i + 1, 3] = 2;
                if (j < tm)
                {
                    for (k = tm - 1; k >= j; k--)
                    {
                        for (p = 0; p <= 6; p++)
                        {
                            Tree[k + 1, p] = Tree[k, p];
                        }
                        Tree[Tree[k, 4], 7] = k + 1;
                    }
                }
                Tree[j, 0] = n;
                Tree[j, 1] = 0;
                Tree[j, 2] = 0;
                Tree[j, 3] = 0;
                Tree[j, 4] = tm;
                Tree[j, 5] = Tree[i, 4];
                Tree[j, 6] = Tree[i + 1, 4];
                Tree[tm, 7] = j;
                tm = tm + 1;
                i = i + 2;
            }
            Tree[i, 2] = tm;
            Tree[i, 3] = 1;

            Tree[i + 1, 2] = tm;
            Tree[i + 1, 3] = 2;
            Tree[tm, 7] = tm;
            Tree[tm, 5] = Tree[i, 4];
            Tree[tm, 6] = Tree[i + 1, 4];
        }
    }
}