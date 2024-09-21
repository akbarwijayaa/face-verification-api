import re
import os
import numpy as np
import cv2
import json
import face_recognition
from PIL import Image, ImageOps
from os.path import dirname, join, abspath
from configparser import ConfigParser


class updateData:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.realpath('__file__'))
        self.models_path = join(self.base_path, 'models')
        self.weight_path = join(self.models_path, 'data.json')
        self.data_path = join(self.base_path, 'data')
        
        self.config = ConfigParser()
        self.config.read(join(self.data_path,'config.ini'))
        self.url_server = self.config['train']['url_server']

    def name(self, no_ind, new_name):
        data = open(self.weight_path)
        rs_json = json.load(data)
        key_detected = []
        
        for key in rs_json.keys():
            res = re.findall(r'\w+', key)
            no_ind_key = res[0]
            if no_ind_key == no_ind:
                img_name_old = self.url_server + '/' + key + '.JPG'
                img_name_new = f'{self.url_server}/{no_ind} {new_name}.JPG'
                os.rename(img_name_old, img_name_new)
                key_detected.append(key)
        
        if key_detected != []:
            for key in key_detected:
                rs_json[f'{no_ind} {new_name}'] = rs_json.pop(key)
                
            with open(self.weight_path, 'w', encoding='utf-8') as js:
                json.dump(rs_json, js, ensure_ascii=False, indent=4)

            return 'Success', 200
        
        else:
            return 'No induk tidak terdaftar', 400
            
    def no_ind(self, no_ind, new_noind):
        data = open(self.weight_path)
        rs_json = json.load(data)
        key_detected = []

        for key in rs_json.keys():
            res = re.findall(r'\w+', key)
            if res[0] == no_ind:
                img_name_old = self.url_server + '/' + key + '.JPG'
                name = ' '.join(res[1:])
                img_name_new = f'{self.url_server}/{new_noind} {name}.JPG'
                os.rename(img_name_old, img_name_new)
                key_detected.append(key)

        if key_detected != []:
            for key in key_detected:
                rs_json[f'{new_noind} {name}'] = rs_json.pop(key)

            with open(self.weight_path, 'w', encoding='utf-8') as js:
                json.dump(rs_json, js, ensure_ascii=False, indent=4)

            return 'Success', 200

        else:
            return 'No induk tidak terdaftar', 400

            
    def find_class_name(self, name, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        images = []
        class_name = []
        no_ind = self.get_data_users()
        user = os.path.splitext(name)[0].upper()
        res = re.findall(r'\w+', user)
        if res[0] in no_ind:
            imgs = Image.fromarray(image)
            imgs = ImageOps.exif_transpose(imgs)
            imgs.save(f'{self.url_server}/{name.upper()}.JPG', 'JPEG')
            images.append(image)
            class_name.append(os.path.splitext(name)[0].upper())
        return images

    def find_encode(self, images):
        try:
            encode_list = []
            for img in images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img, num_jitters=100, model="large")[0]
                encode_list.append(encode.tolist())
            return encode_list
        except:
            encode_list = []
            return encode_list
        
    def face_model(self, no_ind, encode_list):
        data = open(self.weight_path)
        rs_json = json.load(data)
        key_detected = []
        for key in rs_json.keys():
            res = re.findall(r'\w+', key)
            no_ind_key = res[0]
            if no_ind_key == no_ind:
                key_detected.append(key)
        if encode_list != []:
            if key_detected != []:
                for key in key_detected:
                    new_json = {key:encode_list}
                    rs_json.update(new_json)
                    
                with open(self.weight_path, 'w', encoding='utf-8') as js:
                    json.dump(rs_json, js, ensure_ascii=False, indent=4)

                return 'Success', 200
            else:
                return 'No induk tidak terdaftar', 400
        else:
            return 'Wajah tidak terdeteksi', 400
        
    def delete_data(self, no_ind):
        data = open(self.weight_path)
        rs_json = json.load(data)
        key_to_delete = []
        for key in rs_json.keys():
            res = re.findall(r'\w+', key)
            no_ind_key = res[0]
            if no_ind_key == no_ind:
                target = self.url_server + '/' + key + '.JPG'
                os.remove(target)
                key_to_delete.append(key)
        if key_to_delete != []:
            for key in key_to_delete:
                del rs_json[key]

            with open(self.weight_path, 'w', encoding='utf-8') as js:
                json.dump(rs_json, js, ensure_ascii=False, indent=4)

            return 'Success', 200
        else:
            return 'No induk tidak terdaftar', 400
        
    def get_data_users(self):
        if os.listdir(self.models_path) == []:
            arr_users = []
        else:
            data = open(self.weight_path)
            rs_json = json.load(data)
            list_noind = []
            
            for key, value in rs_json.items():
                res = re.findall(r'\w+', key)
                list_noind.append(res[0])
                
            arr_users = np.array(list_noind)
        return arr_users