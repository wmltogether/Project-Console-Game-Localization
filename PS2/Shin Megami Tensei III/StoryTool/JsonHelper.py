import json

class JsonHelper(object):
    @staticmethod
    def Deserialize(obj_dict):
        return json.dumps(obj_dict, default=lambda o: o.__dict__, sort_keys=True ,ensure_ascii=False,indent=4)
        
    @staticmethod
    def Serialize(str_json_data):
        if (str_json_data[0] == u"\uFEFF"):
            str_json_data = str_json_data[1:]
        return json.loads(str_json_data)