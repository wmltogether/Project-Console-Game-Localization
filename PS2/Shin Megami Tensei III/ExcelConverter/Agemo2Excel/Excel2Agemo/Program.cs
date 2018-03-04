using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PFramework;
using System.IO;
using System.Text.RegularExpressions;
using PFramework.Formats;

namespace Excel2Agemo
{
    
    class Program
    {
        public static void Excel2AgemoConv()
        {
            string excelFile = "./DDS3_Translation.xlsx";
            string jpPath = "./jp-text";
            string cnPath = "./cn-text";
            if (!Directory.Exists(jpPath))
            {
                Directory.CreateDirectory(jpPath);
            }
            if (!Directory.Exists(cnPath))
            {
                Directory.CreateDirectory(cnPath);
            }

            if (File.Exists(excelFile))
            {
                ExcelLoader excel = new ExcelLoader(excelFile);
                excel.ReadExcel();
                string[] jpFiles = Directory.GetFiles(jpPath, "*.txt", SearchOption.AllDirectories);
                foreach (var fileName in jpFiles)
                {
                    string fName = Path.GetFileName(fileName);
                    if (File.Exists(jpPath + "/" + fName) && File.Exists(jpPath + "/" + fName))
                    {
                        Console.WriteLine("Reading:" + jpPath + "/" + fName);
                        List<AgemoText.Data> jpData = AgemoText.ReadAgemoText(File.ReadAllLines(jpPath + "/" + fName, Encoding.Unicode));
                        for (int i = 0; i < jpData.Count; i++)
                        {
                            string ctext = jpData[i].Text;
                            string ctag = jpData[i].TAG;
                            string seacrchkey = fName + "__" + ctag;
                            if (DataMgr.Instance.GameTextDictionary.ContainsKey(seacrchkey))
                            {
                                string vtext = DataMgr.Instance.GameTextDictionary[seacrchkey].zh_CN;
                                if (string.IsNullOrEmpty(vtext))
                                {
                                    vtext = ctext;
                                }

                                ctext = vtext;
                                if (ctext.EndsWith("{end}"))
                                {
                                    string[] tval = Regex.Split(ctext, "{end}", RegexOptions.IgnoreCase);
                                    ctext = tval[0]+ "{end}";
                                }
                            }

                            jpData[i].Text = ctext;

                        }

                        string reTextcont = AgemoText.CreateAgemoText(jpData);
                        Console.WriteLine("Writing:" + cnPath + "/" + fName);
                        File.WriteAllText(cnPath + "/" + fName, reTextcont, Encoding.Unicode);

                    }
                    
                }

            }
            else
            {
                Console.WriteLine("{0} 找不到，停止解析", excelFile);
            }
                
        }
        static void Main(string[] args)
        {
            Excel2AgemoConv();
        }
    }
}
