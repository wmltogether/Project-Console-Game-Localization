using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using NPOI.OpenXmlFormats.Dml;
using PFramework;
using PFramework.Formats;


namespace Agemo2Excel
{
    class Program
    {
        public static Dictionary<string, AgemoText.Data> convData(List<AgemoText.Data> cnData)
        {
            var cnDictionary = new Dictionary<string, AgemoText.Data>();
            foreach (AgemoText.Data data in cnData)
            {
                cnDictionary.Add(data.TAG, data);
            }

            return cnDictionary;
        }

        public static void ReadAllAgemo(string cnPath, string jpPath)
        {
            //string cnPath = "./cn-text";
            //string jpPath = "./jp-text";
            string[] cnFiles = Directory.GetFiles(cnPath, "*.txt", SearchOption.AllDirectories);
            Dictionary<string, AgemoText.Data> cnDictionary = new Dictionary<string, AgemoText.Data>();
            
            LocText tempLoc = new LocText("");
            foreach (var fileName in cnFiles)
            {
                string fName = Path.GetFileName(fileName);
                if (File.Exists(cnPath + "/" + fName) && File.Exists(jpPath + "/" + fName))
                {
                    List<AgemoText.Data> cnData = AgemoText.ReadAgemoText(File.ReadAllLines(cnPath + "/" + fName, Encoding.Unicode));
                    List<AgemoText.Data> jpData = AgemoText.ReadAgemoText(File.ReadAllLines(jpPath + "/" + fName, Encoding.Unicode));
                    cnDictionary = convData(cnData);
                    for (int i = 0; i < jpData.Count; i++)
                    {
                        tempLoc = new LocText(jpData[i].Text);
                        if (cnDictionary.ContainsKey(jpData[i].TAG))
                        {
                            tempLoc.zh_CN = cnDictionary[jpData[i].TAG].Text;
                        }
                        DataMgr.Instance.GameTextDictionary.Add(fName + "__" + jpData[i].TAG, tempLoc);
                        
                    }
                }
            }

            ExcelLoader excel = new ExcelLoader("./DDS3_Translation.xlsx");
            excel.WriteExcel(DataMgr.Instance.GameTextDictionary);


        }
        static void Main(string[] args)
        {
            ReadAllAgemo("./cn-text", "./jp-text");
            Console.WriteLine("all done,have fun");
            Console.ReadLine();
        }
    }
}
