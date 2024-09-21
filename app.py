"""
REST API face verification in CV.KHS
"""
import io
import os
import re
import cv2
import json
import time
import flask
import base64
import argparse
import numpy as np
import pandas as pd

from datetime import datetime
from flask import Flask, request
from sqlalchemy import create_engine    
from configparser import ConfigParser
from flask_session import Session
from os.path import dirname, join, abspath
from werkzeug.exceptions import HTTPException

from src.to_dashboard.main import updateApiStatus, appendData


import src.recognizer as recognize
from src.register import Training
from src.getter import DataUser
from src.updater import updateData

app = Flask(__name__)
app.config["DEBUG"] = True

base_path = dirname(abspath(__file__))
data_path = join(base_path, 'src')
config = ConfigParser()
config.read(join(data_path,'config.ini'))


@app.errorhandler(HTTPException)
def handle_exception(e):
    """
    Handle exceptions and return JSON response.
    """
    response = e.get_response()
    response.data = json.dumps({"message": e.description})
    response.content_type = "application/json"
    return response, e.code


@app.route(config['api']['url_login'], methods=["POST", "GET"])
def predict():
    """
    Perform face recognition on the input image.
    """
    start_time = time.time()
    base_path = dirname(abspath(__file__))

    if request.method != "POST":
        response = {
            'status': 'running',
            'message': 'restapi run normally'
        }
        return response, 200

    if request.files.get("image"):
        image_file = request.files["image"]
        image_bytes = image_file.read()
        img_b64 = base64.b64encode(image_bytes)
        nparr = np.frombuffer(base64.b64decode(img_b64), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        rec = recognize.recognizer()
        result, code = rec.predict(image)
        result['time'] = round(time.time() - start_time, 2)
        ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        appendData(
                   id_api=1, 
                   ip_address = ip_addr,
                   request_date=datetime.now(), 
                   url_api=request.url,
                   response=result,
                   response_time=round((time.time() - start_time)*100)
                )
        return result, code


@app.route(config['api']['url_registration'], methods=["POST", "GET"])
def register():
    """
    Register a new face with associated data.
    """
    base_path = dirname(abspath(__file__))
    train_path = join(base_path, 'train')

    if request.method != "POST":
        return "Register new face"

    img_name = request.form.get("no_ind").upper()
    urls_image = config['api']['url_img'] + img_name + '.JPG'

    if request.files.get("image"):
        image_file = request.files["image"]
        image_bytes = image_file.read()
        img_b64 = base64.b64encode(image_bytes)
        nparr = np.frombuffer(base64.b64decode(img_b64), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    train = Training()
    img, class_name = train.find_class_name(image, img_name)
    encode_list = train.find_encode(img)

    if encode_list != []:
        train.append_json(class_name, encode_list)
        res = re.findall(r'\w+', img_name)
        name = ' '.join(res[1:])

        result = {
            "registration_number": res[0],
            "name": name,
            "image": urls_image
        }

        response = flask.jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response, 200
    else:
        result = {
            "registration_number": [],
            "name": [],
            "image": []
        }

        response = flask.jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response, 200


@app.route(config['api']['url_data_user'], methods=["GET"])
def get_data(): 
    """
    Get sorted user data.
    """
    data = DataUser()
    data_result = data.get_sorted_data()
    response = data_result

    response = flask.jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response, 200


@app.route(config['api']['url_update_name'], methods=["PUT"])
def update_name():
    """
    Update user's name.
    """
    no_ind = request.form.get("no_ind").upper()
    new_name = request.form.get("new_name").upper()
    upd = updateData()
    msg, code = upd.name(no_ind=no_ind, new_name=new_name)
    if code == 200:
        result = {
            'success': True
        }
    else:
        result = {
            'success': False,
            'message': msg
        }

    response = flask.jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response, code


@app.route(config['api']['url_update_noind'], methods=["PUT"])
def update_noind():
    """
    Update user's registration number.
    """
    no_ind = request.form.get("no_ind").upper()
    new_noid = request.form.get("new_noid").upper()
    upd = updateData()

    msg, code = upd.no_ind(no_ind=no_ind, new_noind=new_noid)
    if code == 200:
        result = {
            'success': True
        }
    elif code == 400:
        result = {
            'success': False,
            'message': msg
        }

    response = flask.jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response, code


@app.route(config['api']['url_update_face'], methods=["PUT"])
def update_face_encode():
    """
    Update user's face encoding.
    """
    base_path = dirname(abspath(__file__))
    update_path = join(base_path, 'update')
    models_path = join(base_path, 'models')
    weight_path = join(models_path, 'data.json')

    no_ind = request.form.get("no_ind").upper()
    data = open(weight_path)
    rs_json = json.load(data)

    image_name = []
    
    for key in rs_json.keys():
        res = re.findall(r'\w+', key)
        no_ind_key = res[0]
        if no_ind_key == no_ind:
            image_name.append(key)
            
    name = image_name[0]
    # print(name)
    if request.files.get("image"):
        image_file = request.files["image"]
        image_bytes = image_file.read()
        img_b64 = base64.b64encode(image_bytes)
        nparr = np.frombuffer(base64.b64decode(img_b64), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    upd = updateData()
    img = upd.find_class_name(name, image)
    encode_list = upd.find_encode(img)
    msg, code = upd.face_model(no_ind=no_ind, encode_list=encode_list)
    if code == 200:
        result = {
            'success': True
        }
    elif code == 400:
        result = {
            'success': False,
            'message': msg
        }

    response = flask.jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response, code


@app.route(config['api']['url_delete_data'], methods=["DELETE"])
def delete():
    """
    Delete user's data.
    """
    no_ind = request.form.get("no_ind").upper()
    upd = updateData()
    msg, code = upd.delete_data(no_ind=no_ind)
    if code == 200:
        result = {
            'success': True
        }
    elif code == 400:
        result = {
            'success': False,
            'message': msg
        }

    response = flask.jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response, code


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Flask API face recognition model")
        parser.add_argument("--port", default=5000, type=int, help="port number")
        args = parser.parse_args()
        updateApiStatus(1, 'Active')
        app.run(host="0.0.0.0", port=args.port)
    finally:
        updateApiStatus(1, 'Inactive')
