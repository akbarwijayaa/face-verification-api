import os
import re
import json
import numpy as np
from os.path import dirname, join, abspath
from configparser import ConfigParser


class DataUser:
    def __init__(self):        
        base_path = os.path.dirname(os.path.realpath('__file__'))
        models_path = join(base_path, 'models')
        self.weight_path = join(models_path, 'data.json')
        self.data_path = join(base_path, 'data')
        
        self.config = ConfigParser()
        self.config.read(join(self.data_path,'config.ini'))
        self.url_img = self.config['api']['url_img']
    
    def get_data(self):
        data = open(self.weight_path)
        rs_json = json.load(data)
        result = {
            "data":[]
        }
        for key, value in rs_json.items():
            res = re.findall(r'\w+', key)
            name = ' '.join(res[1:])
            img_url = self.url_img + key + '.JPG'
            r1 = {
                    "registration_number": res[0],
                    "name": name,
                    "image": img_url
            }
            result['data'].append(r1)
        return result
    
    def get_sorted_data(self):
        data = self.get_data()
        no_induk = []
        for value in data.values():
            for id_pekerja in value:
                idp = id_pekerja['registration_number']
                no_induk.append(idp)

        no_induk.sort()
        ind_arr = np.array(no_induk)

        data_sorted = {
            "data":[]
        }
        for at in ind_arr:
            for data_dict in data['data']:
                if data_dict['registration_number'] == at:
                    data_sorted['data'].append(data_dict)

        return data_sorted