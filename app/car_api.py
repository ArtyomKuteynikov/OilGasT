# api.py
import json
from flask import Blueprint, request, current_app, url_for, redirect
from werkzeug.security import generate_password_hash
import base64
from PIL import Image
from io import BytesIO
from . import db
from .models import User, Codes
from iqsms_rest import Gate
import random
import time
from .config import *
from os import getcwd

api = Blueprint('car_api', __name__)


@api.route('/api/my-cars')
def my_cars():
    '''
    ---
   get:
     summary: Мои машины
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: OPMrexrW7r9vdO0D$36e5126f0fe9fa66bd278c8c25dd3ad319179a0edf5de678f58a95a0042b343d
           description: token
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   cars:
                     type: array
                     items:
                       type: object
                       properties:
                           model:
                             type: string
                           num:
                             type: string
                           color:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                                   code:
                                     type: string
                           oil:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                           petrol:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                           insurance:
                             type: string
                           additional:
                             type: array
                             items:
                               type: object
                               properties:
                                   name:
                                     type: string
                                   value:
                                     type: string
       '400':
         description: Не передан обязательный параметр
         content:
           application/json:
             schema: ErrorSchema
       '401':
         description: Неверный токен
         content:
           application/json:
             schema: ErrorSchema
       '403':
         description: Пользователь заблокирован
         content:
           application/json:
             schema: ErrorSchema
     tags:
       - cars
    '''
    token = request.args.get('token')

    return current_app.response_class(
        response=json.dumps(
            {
                'cars': [
                    {
                        'model': 'Mercedes E200',
                        'num': 'В777ВВ 77',
                        'color': {
                            'id': 1,
                            'name': 'черный',
                            'code': '#000000'
                        },
                        'oil': {
                            'id': 1,
                            'name': 'Обычное масло'
                        },
                        'petrol': {
                            'id': 1,
                            'name': 'FB95 Евро+'
                        },
                        'insurance': '10.10.2023',
                        'additional': [
                            {
                                'name': 'Поле 1',
                                'value': 'Значение 1'
                            }
                        ]
                    },
                ],
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/add-car', methods=['POST'])
def add_car():
    """
   ---
   post:
     summary: Добавить машину
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: OPMrexrW7r9vdO0D$36e5126f0fe9fa66bd278c8c25dd3ad319179a0edf5de678f58a95a0042b343d
           description: token
     requestBody:
        required: true
        content:
          application/json:
              schema:
                type: object
                properties:
                   model:
                     type: string
                   num:
                     type: string
                   color:
                     type: integer
                   oil:
                     type: integer
                   petrol:
                     type: integer
                   insurance:
                     type: number
                   additional:
                     type: string
                example:   # Sample object
                  model: Mercedes E200
                  num: В777ВВ 77
                  color: 1
                  oil: 1
                  petrol: 1
                  insurance: 1682077262.288192
                  additional:
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   cars:
                     type: array
                     items:
                       type: object
                       properties:
                           model:
                             type: string
                           num:
                             type: string
                           color:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                                   code:
                                     type: string
                           oil:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                           petrol:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                           insurance:
                             type: string
                           additional:
                             type: array
                             items:
                               type: object
                               properties:
                                   name:
                                     type: string
                                   value:
                                     type: string
       '400':
         description: Не передан обязательный параметр
         content:
           application/json:
             schema: ErrorSchema
       '401':
         description: Неверный токен
         content:
           application/json:
             schema: ErrorSchema
       '403':
         description: Пользователь заблокирован
         content:
           application/json:
             schema: ErrorSchema
     tags:
       - cars
    """
    token = request.args.get('token')
    model = request.json.get('model')
    num = request.json.get('num')
    vin = request.json.get('vin')
    color = request.json.get('color')
    oil = request.json.get('color')
    petrol_type = request.json.get('petrol_type')
    ensurance = request.json.get('ensurance')
    additional = request.json.get('additional')


    return redirect(url_for('car_api.my_cars'))


@api.route('/api/edit-car')
def edit_car():
    """
    ---
   post:
     summary: Редактировать машину
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: OPMrexrW7r9vdO0D$36e5126f0fe9fa66bd278c8c25dd3ad319179a0edf5de678f58a95a0042b343d
           description: token
         - in: query
           name: car_id
           schema:
             type: integer
             example: 1
           description: car_id
     requestBody:
        content:
          application/json:
              schema:
                type: object
                properties:

                   model:
                     type: string
                   num:
                     type: string
                   color:
                     type: integer
                   oil:
                     type: integer
                   petrol:
                     type: integer
                   insurance:
                     type: number
                   additional:
                     type: string
                example:   # Sample object

                  model: Mercedes E200
                  num: В777ВВ 77
                  color: 1
                  oil: 1
                  petrol: 1
                  insurance: 1682077564.424564
                  additional:
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   cars:
                     type: array
                     items:
                       type: object
                       properties:
                           model:
                             type: string
                           num:
                             type: string
                           color:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                                   code:
                                     type: string
                           oil:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                           petrol:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                           insurance:
                             type: string
                           additional:
                             type: array
                             items:
                               type: object
                               properties:
                                   name:
                                     type: string
                                   value:
                                     type: string
       '400':
         description: Не передан обязательный параметр
         content:
           application/json:
             schema: ErrorSchema
       '401':
         description: Неверный токен
         content:
           application/json:
             schema: ErrorSchema
       '403':
         description: Пользователь заблокирован
         content:
           application/json:
             schema: ErrorSchema
     tags:
       - cars
    """
    token = request.args.get('token')
    car_id = request.json.get('car_id')
    model = request.json.get('model')
    num = request.json.get('num')
    vin = request.json.get('vin')
    color = request.json.get('color')
    oil = request.json.get('color')
    petrol_type = request.json.get('petrol_type')
    GSM_type = request.json.get('GSM_type')
    ensurance = request.json.get('ensurance')
    additional = request.json.get('additional')

    return redirect(url_for('car_api.my_cars'))


@api.route('/api/delete-car')
def delete_car():
    '''
    ---
   get:
     summary: Удалить машину
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: OPMrexrW7r9vdO0D$36e5126f0fe9fa66bd278c8c25dd3ad319179a0edf5de678f58a95a0042b343d
           description: token
         - in: query
           name: car_id
           schema:
             type: integer
             example: 1
           description: car_id
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   cars:
                     type: array
                     items:
                       type: object
                       properties:
                           model:
                             type: string
                           num:
                             type: string
                           color:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                                   code:
                                     type: string
                           oil:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                           petrol:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                           insurance:
                             type: string
                           additional:
                             type: array
                             items:
                               type: object
                               properties:
                                   name:
                                     type: string
                                   value:
                                     type: string
       '400':
         description: Не передан обязательный параметр
         content:
           application/json:
             schema: ErrorSchema
       '401':
         description: Неверный токен
         content:
           application/json:
             schema: ErrorSchema
       '403':
         description: Пользователь заблокирован
         content:
           application/json:
             schema: ErrorSchema
     tags:
       - cars
    '''
    token = request.args.get('token')
    car_id = request.args.get('car_id')

    return redirect(url_for('car_api.my_cars'))


@api.route('/api/colors')
def colors():
    '''
       ---
   get:
     summary: Цвета
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: OPMrexrW7r9vdO0D$36e5126f0fe9fa66bd278c8c25dd3ad319179a0edf5de678f58a95a0042b343d
           description: token
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   data:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: integer
                           name:
                             type: string
                           code:
                             type: string
       '400':
         description: Не передан обязательный параметр
         content:
           application/json:
             schema: ErrorSchema
       '401':
         description: Неверный токен
         content:
           application/json:
             schema: ErrorSchema
       '403':
         description: Пользователь заблокирован
         content:
           application/json:
             schema: ErrorSchema
     tags:
       - cars
    '''
    return current_app.response_class(
        response=json.dumps(
            {
                'data': [
                    {
                        'id': 1,
                        'name': 'черный',
                        'code': '#000000'
                    },
                    {
                        'id': 2,
                        'name': 'белый',
                        'code': '#ffffff'
                    }
                ]
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/oils')
def oils():
    '''
    ---
   get:
     summary: Масла
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: OPMrexrW7r9vdO0D$36e5126f0fe9fa66bd278c8c25dd3ad319179a0edf5de678f58a95a0042b343d
           description: token
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   data:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: integer
                           name:
                             type: string
       '400':
         description: Не передан обязательный параметр
         content:
           application/json:
             schema: ErrorSchema
       '401':
         description: Неверный токен
         content:
           application/json:
             schema: ErrorSchema
       '403':
         description: Пользователь заблокирован
         content:
           application/json:
             schema: ErrorSchema
     tags:
       - cars
    '''
    return current_app.response_class(
        response=json.dumps(
            {
                'data': [
                    {
                        'id': 1,
                        'name': 'масло',
                    },
                ]
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/petrols')
def petrols():
    '''
    ---
   get:
     summary: Типы топлива
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: OPMrexrW7r9vdO0D$36e5126f0fe9fa66bd278c8c25dd3ad319179a0edf5de678f58a95a0042b343d
           description: token
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   data:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: integer
                           name:
                             type: string
       '400':
         description: Не передан обязательный параметр
         content:
           application/json:
             schema: ErrorSchema
       '401':
         description: Неверный токен
         content:
           application/json:
             schema: ErrorSchema
       '403':
         description: Пользователь заблокирован
         content:
           application/json:
             schema: ErrorSchema
     tags:
       - cars
    '''
    return current_app.response_class(
        response=json.dumps(
            {
                'data': [
                    {
                        'id': 1,
                        'name': '95',
                    },
                ]
            }
        ),
        status=200,
        mimetype='application/json'
    )