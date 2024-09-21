from asyncio.constants import ACCEPT_RETRY_DELAY
import dlib
import cv2
import numpy as np
import sys
import os
import re
import json
from os.path import dirname, join, abspath
from PIL import Image, ImageOps
import time
import face_recognition
import matplotlib.pyplot as plt
from configparser import ConfigParser


class Training:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.realpath('__file__'))
        self.models_path = join(self.base_path, 'models')
        self.src_path = join(self.base_path, 'src')
        self.weight_path = join(self.models_path, 'face_embeddings.json')
        
        self.config = ConfigParser()
        self.config.read(join(self.src_path,'config.ini'))
        self.url_server = self.config['train']['url_server']
            
    def find_class_name(self, image, img_name):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        images = []
        no_induk = []
        class_name = []
        no_ind = self.get_data_users()
        user = os.path.splitext(img_name)[0].upper()
        res = re.findall(r'\w+', user)
        if res[0] not in no_ind:
            imgs = Image.fromarray(image)
            imgs = ImageOps.exif_transpose(imgs)
            # imgs.save(f'{self.url_server}/{img_name.upper()}.JPG', 'JPEG')
            images.append(image)
            no_induk.append(res[0])
            class_name.append(os.path.splitext(img_name)[0].upper())
        return images, class_name

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
    
    def append_json(self, class_name, encode_list):
        if os.listdir(self.models_path) == []:
            result = {}
            for item in class_name:
                result[item]=encode_list
            with open(self.weight_path, 'w', encoding='utf-8') as js:
                json.dump(result, js, ensure_ascii=False, indent=4)
            
        else:
            data = open(self.weight_path)
            rs_json = json.load(data)
            for item in class_name:
                rs_json[item]=encode_list

            with open(self.weight_path, 'w', encoding='utf-8') as js:
                json.dump(rs_json, js, ensure_ascii=False, indent=4)
                      
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