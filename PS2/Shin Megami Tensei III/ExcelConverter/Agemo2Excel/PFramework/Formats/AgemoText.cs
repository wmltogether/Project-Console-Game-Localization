using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PFramework.Formats
{
    public class AgemoText
    {
        
        public static List<Data> ReadAgemoText(string[] lines)
        {
            List<Data> DataList = new List<Data>();
            var num = lines.Length;
            int index = 0;
            string line = "";
            string tmp = "";
            int i = 0;
            for (int x = 0; x < num; x++)
            {
                if (!lines[x].Contains("####"))
                {
                    continue;
                }
                Data data = new Data();
                index = x;
                line = lines[x];
                tmp = line.Substring(5, line.Length - 1 - 5 - 3);
                data.TAG = tmp;
                i = 1;
                tmp = "";
                while (true)
                {
                    if (index + i >= num)
                    {
                        break;
                    }

                    if (lines[index + i].Contains("####"))
                    {
                        break;
                    }
                    tmp += (lines[index + i] + "\r\n");
                    i += 1;
                    
                }
                
                data.Text = (tmp.Remove(tmp.Length - 4));
                DataList.Add(data);
            }
            return DataList;
        }

        public static string CreateAgemoText(List<Data> values)
        {
            StringBuilder builder = new StringBuilder();
            foreach (var data in values)
            {
                string ttag = data.TAG;
                string ttext = data.Text;
                if (ttag.EndsWith(" "))
                {
                    ttag = ttag.Remove(ttag.Length - 1);
                }

                ttext = ttext.Replace("\r", "");
                ttext = ttext.Replace("\n", "\r\n");


                string dst = string.Format("#### {0} ####\r\n{1}\r\n\r\n", ttag, ttext);
                builder.Append(dst);
            }
            return builder.ToString();
        }

        public class Data
        {
            public string TAG;
            public string Text;
        }

    }
}
