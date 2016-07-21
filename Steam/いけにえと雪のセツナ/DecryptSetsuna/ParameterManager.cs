using System.IO;
using System.Security.Cryptography;
using System.Text;

namespace DecryptSetsuna
{
    public class ParameterManager
    {
        public static byte[] DecryptParameter(byte[] data)
        {
            {
                RijndaelManaged managed = new RijndaelManaged();
                byte[] bytes = Encoding.UTF8.GetBytes("8xTD|EgD|b?07QDj");
                byte[] buffer2 = Encoding.UTF8.GetBytes("/]s@*CxLzM!9Qd%(");
                return managed.CreateDecryptor(bytes, buffer2).TransformFinalBlock(data, 0, data.Length);
            }
            return data;
        }

        public static byte[] EncryptParameter(byte[] data)
        {
            RijndaelManaged managed = new RijndaelManaged();
            byte[] bytes = Encoding.UTF8.GetBytes("8xTD|EgD|b?07QDj");
            byte[] buffer2 = Encoding.UTF8.GetBytes("/]s@*CxLzM!9Qd%(");
            return managed.CreateEncryptor(bytes, buffer2).TransformFinalBlock(data, 0, data.Length);

        }

    }
}