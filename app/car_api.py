# api.py
import datetime
import os

import pandas as pd
import json
from flask import Blueprint, request, current_app, url_for, redirect
from werkzeug.security import generate_password_hash
import base64
from PIL import Image
from io import BytesIO
from .static_dicts import goods
from . import db
from .models import User, Codes, Cars, Brands, Model
from iqsms_rest import Gate
import random
import time
from .config import *
from os import getcwd

api = Blueprint('car_api', __name__)


@api.route('/api/init/')
def init():
    print(os.getcwd())
    df = pd.read_json(f'{os.getcwd()}/app/carsBrands.json')
    for i in df.values:
        new_brand = Brands(name=i[0], url=i[1])
        db.session.add(new_brand)
        db.session.commit()
        for j in i[2]:
            new_model = Model(name=j['model'], url=j['href'], brand=new_brand.id)
            db.session.add(new_model)
            db.session.commit()
    return 'success'


@api.route('/api/brands')
def brands_get():
    '''
    ---
   get:
     summary: Марки
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   brands:
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
    brands = Brands.query.filter_by().all()
    return {
        'brands': [{'id': i.id, 'name': i.name} for i in brands]
    }


@api.route('/api/models')
def models_get():
    '''
    ---
   get:
     summary: Модели
     parameters:
         - in: query
           name: brand
           schema:
             type: integer
             example: 3
           description: brand
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   models:
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
    id = request.args.get('brand')
    models = Model.query.filter_by(brand=id).all()
    return {
        'models': [{'id': i.id, 'name': i.name} for i in models]
    }


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
             example: xv2ossY6V9fikmjp$a45f9c93467deca882d3219ba4c568e3a9ebe4a53dbd17b03ec6987a9976b8bc
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
                           id:
                             type: integer
                           brand:
                             type: object
                             properties:
                                   name:
                                     type: string
                                   id:
                                     type: integer
                           model:
                             type: object
                             properties:
                                   name:
                                     type: string
                                   id:
                                     type: integer
                           num:
                             type: string
                           color:
                             type: string
                           oil:
                             type: integer
                           petrol:
                             type: object
                             properties:
                                   id:
                                     type: integer
                                   name:
                                     type: string
                           ensurance:
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
    user = User.query.filter_by(token=token).first()
    if not user:
        return current_app.response_class(
            response=json.dumps(
                {'error': f'USER DOES NOT EXIST'}
            ),
            status=403,
            mimetype='application/json'
        )
    if user.status == "blocked":
        return current_app.response_class(
            response=json.dumps(
                {'error': "USER BLOCKED"}
            ),
            status=403,
            mimetype='application/json'
        )
    cars = []
    cars_raw = Cars.query.filter_by(user_id=user.id).all()
    for car in cars_raw:
        cars.append(
            {
                'id': car.id,
                'brand': {
                    'name': Brands.query.filter_by(id=car.brand).first().name if Brands.query.filter_by(
                        id=car.brand).first() else '',
                    'id': car.brand
                },
                'model': {
                    'name': Model.query.filter_by(id=car.model).first().name if Model.query.filter_by(
                        id=car.model).first() else '',
                    'id': car.model
                },
                'num': car.num,
                'color': car.color,
                'petrol': {
                    'id': car.petrol_type,
                    'name': goods[str(car.petrol_type)] if str(car.petrol_type) in goods else 'NOT FOUND'
                },
                'ensurance': car.ensurance.strftime('%d-%m-%Y') if car.ensurance else '',
                'additional': json.loads(car.additional)
            }
        )
    return current_app.response_class(
        response=json.dumps(
            {
                'cars': cars,
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/add-car', methods=['POST'])
def add_car():
    '''
    ---
   post:
     summary: Добавить машину
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: xv2ossY6V9fikmjp$a45f9c93467deca882d3219ba4c568e3a9ebe4a53dbd17b03ec6987a9976b8bc
           description: token
     requestBody:
        content:
          application/json:
              schema:
                type: object
                properties:
                   brand:
                     type: integer
                   model:
                     type: integer
                   num:
                     type: string
                   color:
                     type: string
                   petrol_type:
                     type: integer
                   insurance:
                     type: string
                   additional:
                     type: string
                example:   # Sample object

                  brand: 1
                  model: 1
                  num: В777ВВ 77
                  color: белый
                  petrol_type: 92
                  insurance: 30-08-2023
                  additional:
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   success:
                     type: boolean
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
    user = User.query.filter_by(token=token).first()
    if not user:
        return current_app.response_class(
            response=json.dumps(
                {'error': f'USER DOES NOT EXIST'}
            ),
            status=403,
            mimetype='application/json'
        )
    if user.status == "blocked":
        return current_app.response_class(
            response=json.dumps(
                {'error': "USER BLOCKED"}
            ),
            status=403,
            mimetype='application/json'
        )
    brand = request.json.get('brand')
    model = request.json.get('model')
    num = request.json.get('num')
    vin = request.json.get('vin')
    color = request.json.get('color')
    petrol_type = request.json.get('petrol_type')
    ensurance = datetime.datetime.strptime(request.json.get('insurance'), '%d-%m-%Y') if request.json.get(
        'insurance') else ''
    additional = request.json.get('additional')
    new_car = Cars(user_id=user.id, brand=brand, model=model, num=num, vin=vin, color=color, petrol_type=petrol_type,
                   ensurance=ensurance, additional=json.dumps(additional))
    db.session.add(new_car)
    db.session.commit()
    return current_app.response_class(
        response=json.dumps(
            {
                'success': True,
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/edit-car', methods=['PUT', 'POST'])
def edit_car():
    '''
    ---
   put:
     summary: Редактировать машину
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: xv2ossY6V9fikmjp$a45f9c93467deca882d3219ba4c568e3a9ebe4a53dbd17b03ec6987a9976b8bc
           description: token
         - in: query
           name: car_id
           schema:
             type: string
             example: 1
           description: car_id
     requestBody:
        content:
          application/json:
              schema:
                type: object
                properties:

                   brand:
                     type: integer
                   model:
                     type: integer
                   num:
                     type: string
                   color:
                     type: string
                   petrol_type:
                     type: integer
                   insurance:
                     type: string
                   additional:
                     type: string
                example:   # Sample object

                  brand: 1
                  model: 1
                  num: В777ВВ 77
                  color: белый
                  petrol_type: 92
                  insurance: 30-08-2023
                  additional:
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   error:
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
    user = User.query.filter_by(token=token).first()
    if not user:
        return current_app.response_class(
            response=json.dumps(
                {'error': f'USER DOES NOT EXIST'}
            ),
            status=403,
            mimetype='application/json'
        )
    if user.status == "blocked":
        return current_app.response_class(
            response=json.dumps(
                {'error': "USER BLOCKED"}
            ),
            status=403,
            mimetype='application/json'
        )

    car_id = request.args.get('car_id')
    if not Cars.query.filter_by(id=car_id, user_id=user.id).first():
        return current_app.response_class(
            response=json.dumps(
                {'error': "NOT YOUR CAR!!!"}
            ),
            status=403,
            mimetype='application/json'
        )
    brand = request.json.get('brand')
    model = request.json.get('model')
    num = request.json.get('num')
    vin = request.json.get('vin')
    color = request.json.get('color')
    petrol_type = request.json.get('petrol_type')
    ensurance = datetime.datetime.strptime(request.json.get('insurance'), '%d-%m-%Y') if request.json.get(
        'insurance') else ''
    additional = request.json.get('additional')
    _ = Cars.query.filter_by(id=car_id).update(
        {'brand': brand, 'model': model, 'num': num, 'vin': vin, 'color': color, 'petrol_type': petrol_type,
         'ensurance': ensurance, 'additional': json.dumps(additional)})
    db.session.commit()
    return current_app.response_class(
        response=json.dumps(
            {
                'success': True,
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/delete-car', methods=['DELETE'])
def delete_car():
    '''
    ---
   delete:
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
                        "id": "92",
                        "name": "АИ-92"
                    },
                    {
                        "id": "93",
                        "name": "АИ-92 Евро"
                    },
                    {
                        "id": "95",
                        "name": "АИ-95"
                    },
                    {
                        "id": "98",
                        "name": "АИ-98"
                    },
                    {
                        "id": "40",
                        "name": "ДТ"
                    },
                    {
                        "id": "50",
                        "name": "ДТ Евро"
                    },
                    {
                        "id": "45",
                        "name": "ДТ Экто"
                    }
                ]
            }
        ),
        status=200,
        mimetype='application/json'
    )
