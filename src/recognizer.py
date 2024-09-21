import cv2
import re
import os
import json
import numpy as np
import face_recognition

from configparser import ConfigParser
from os.path import dirname, join, abspath, realpath

class recognizer:
    def __init__(self):
        self.base_path = dirname(dirname(abspath(__file__)))
        self.src_path = join(self.base_path, 'src')
        self.models_path = join(self.base_path, 'models')
        self.weight_path = join(self.models_path, 'face_embeddings.json')
        
        self.config = ConfigParser()
        self.config.read(join(self.src_path,'config.ini'))

        self.face_encode, self.list_face_encode = self.load_model()

    def load_model(self):
        data = open(self.weight_path)
        face_encode = json.load(data)
        list_face_encode = [data[0] for data in face_encode.values()]
        return face_encode, list_face_encode
            
    def predict(self, img_nparr):
        img_rgb = cv2.cvtColor(img_nparr, cv2.COLOR_BGR2RGB)
        face_loc = face_recognition.face_locations(img_rgb)
        encode_images = face_recognition.face_encodings(img_rgb, face_loc)
        try:
            for encode_face, face_loc in zip(encode_images, face_loc):
                matches = face_recognition.compare_faces(self.list_face_encode, encode_face)
                face_dist = face_recognition.face_distance(self.list_face_encode, encode_face)
                face_dist_min = np.amin(face_dist)  
                if face_dist_min < float(self.config['params']['face_dist_min']): 
                    match_index = np.argmin(face_dist)
                for key, value in self.face_encode.items():
                    if value[0] == self.list_face_encode[match_index]:
                        res = re.findall(r'\w+', key)
                        name = ' '.join(res[1:])
                        result = {
                            'message': self.config['response']['success_msg'],
                            'data': {
                                'registration_number': res[0],
                                'name': name
                            }
                        }                       
            return result, self.config['response']['success_code']

        except Exception as a:
            result = {
                'message': self.config['response']['fail_msg'],
                'data': None
            }
            return result, self.config['response']['fail_code']
