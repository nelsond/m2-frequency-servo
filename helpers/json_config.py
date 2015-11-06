# -*- coding: utf-8 -*-
import json, datetime

def json_date_handler(obj):
    return obj.strftime('%Y-%m-%dT%H:%M:%S') if hasattr(obj, 'strftime') else obj

class JSONConfig:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {}
        self.load()

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, item, value):
        self.data[item] = value

    def load(self):
        f = open(self.file_path, 'r')
        json_data = f.read()
        f.close()

        self.data = json.loads(json_data)

    def save(self):
        json_data = json.dumps(self.data,
                indent=2,
                default=json_date_handler)

        f = open(self.file_path, 'w')
        f.write(json_data)
        f.close
