using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;

namespace PFramework
{
    public class SingletonCreator
    {

        public static T CreateSingleton<T>() where T : class, ISingleton
        {
            T retInstance = default(T);

            ConstructorInfo[] ctors = typeof(T).GetConstructors(BindingFlags.Instance | BindingFlags.NonPublic);
            ConstructorInfo ctor = Array.Find(ctors, c => c.GetParameters().Length == 0);

            if (ctor == null)
            {
                throw new Exception("Non-public ctor() not found! in " + typeof(T));
            }

            retInstance = ctor.Invoke(null) as T;

            retInstance.OnSingletonInit();

            return retInstance;
        }
    }

}
