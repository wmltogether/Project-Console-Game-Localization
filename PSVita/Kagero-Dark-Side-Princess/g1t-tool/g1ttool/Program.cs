using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.IO;
using System.Threading.Tasks;

namespace g1ttool
{
    class Program
    {
        [DllImport("user32.dll", EntryPoint = "MessageBox")]
        public static extern int MsgBox(IntPtr hwnd, string text, string caption, uint type);
        public static void ShowMsgBox(string msg)
        {
            MsgBox(IntPtr.Zero, msg, "G1Ttool", 1);
        }

        private static void ShowArgsMsg()
        {
            string msg = 
            "error: no args\n" +
            "====================\n" + 
            "simple g1t dxt5 swizzle export\n" +
            "gen g1t dxt5 swizzled block to png.\n" +
            "PSVita DXTC decompress method from xdanieldzd's ScarletConvert\n" +
            " Usage:\n" +
            "g1ttool <xxx.g1t>\n";
            Console.WriteLine(msg);
        }
        [STAThread]
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                ShowArgsMsg();


                Program.ShowMsgBox("Error: no args \n  Please use this program in console!");

                return;
            }
            if (args.Length > 0)
            {
                string name = args[0];
                G1T g1texture = new G1T(File.ReadAllBytes(name));
                for (int i = 0; i < g1texture.texture_bmps.Length; i++)
                {
                    int position = g1texture.textureInfo.p_offsets[i];
                    string dst = string.Format("{0}.{1:X8}.DXT5.SWIZZLED.PNG", name, position);
                    g1texture.texture_bmps[i].Save(dst);
                }
            }

        }
    }
}
