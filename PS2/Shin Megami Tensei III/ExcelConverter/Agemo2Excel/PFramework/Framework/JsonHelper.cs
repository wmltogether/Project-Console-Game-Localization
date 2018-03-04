using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PFramework
{
    public class JsonHelper
    {
        public static string Serialize(object inputClass)
        {
            string jsondata = JsonConvert.SerializeObject(inputClass, Formatting.Indented);
            return jsondata;
        }

        internal static T Deserialize<T>(string json) where T : class
        {
            json = json.Trim(new char[] { '\uFEFF' });
            JsonSerializer serializer = new JsonSerializer();
            serializer.MissingMemberHandling = MissingMemberHandling.Ignore;
            StringReader sr = new StringReader(json);
            object obj = serializer.Deserialize(new JsonTextReader(sr), typeof(T));
            T t = obj as T;
            return t;
        }
    }
}
