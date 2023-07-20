# api.py
import json
import requests
from flask import Blueprint, request, current_app
from werkzeug.security import generate_password_hash
from . import db
from .models import User
import time

api = Blueprint('map_api', __name__)


def format_phone_number(phone_number):
    # Удаление всех символов, кроме цифр
    phone_number = ''.join(filter(str.isdigit, phone_number))

    # Проверка длины номера телефона
    if len(phone_number) != 11:
        return phone_number  # Возвращаем исходную строку, если длина некорректна

    # Форматирование номера телефона в виде "7-XXX-XXX-XX-XX"
    formatted_phone_number = f"7-{phone_number[1:4]}-{phone_number[4:7]}-{phone_number[7:9]}-{phone_number[9:11]}"

    return formatted_phone_number


@api.route('/api/map')
def get_map():
    '''
    ---
   get:
     summary: Карта АЗС
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   AzsList:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: integer
                           name:
                             type: string
                           addres:
                             type: string
                           petrols:
                             type: array
                             items:
                               type: object
                               properties:
                                   name:
                                     type: string
                                   price:
                                     type: number
                           services:
                             type: array
                             items:
                               type: string
                           lat:
                             type: number
                           lon:
                             type: number
       '400':
         description: Ошибка запроса
         content:
           application/json:
             schema: ErrorSchema
     tags:
       - map
    '''
    try:
        return current_app.response_class(
            response=json.dumps(
                {'AzsList': [
                    {

                        'id': 1,
                        'name': "АЗС \"САМБЕК\"",
                        'addres': "Таганрог, ул. Центральная, 20",
                        'petrols': [
                            {
                                'name': '95',
                                'price': 42.30
                            },
                            {
                                'name': '95',
                                'price': 42.30
                            },
                        ],
                        'services': ["wash", "market", "cafe"],
                        'lat': 47.433274431304454,
                        'lon': 38.931525186505986,
                    },
                    {
                        'id': 2,
                        'name': "АЗС \"САМБЕК\"",
                        'addres': "Таганрог, ул. Центральная, 20",
                        'petrols': [
                            {
                                'name': '95',
                                'price': 42.30
                            },
                            {
                                'name': '95',
                                'price': 42.30
                            },
                        ],
                        'services': ["wash", "market", "cafe"],
                        'lat': 47.20153765412612,
                        'lon': 38.696871286505996,
                    },
                    {
                        'id': 3,
                        'name': "АЗС \"САМБЕК\"",
                        'addres': "Таганрог, ул. Центральная, 20",
                        'petrols': [
                            {
                                'name': '95',
                                'price': 42.30
                            },
                            {
                                'name': '95',
                                'price': 42.30
                            },
                        ],
                        'services': ["wash", "market", "cafe"],
                        'lat': 47.2758928986386,
                        'lon': 38.8539399,
                    },
                    {
                        'id': 4,
                        'name': "АЗС \"САМБЕК\"",
                        'addres': "Таганрог, ул. Центральная, 20",
                        'petrols': [
                            {
                                'name': '95',
                                'price': 42.30
                            },
                            {
                                'name': '95',
                                'price': 42.30
                            },
                        ],
                        'services': ["wash", "market", "cafe"],
                        'lat': 47.318622189650625,
                        'lon': 39.024862999999996,
                    },
                ]}
            ),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return current_app.response_class(
            response=json.dumps(
                {'error': f'ERROR: {e}!'}
            ),
            status=400,
            mimetype='application/json'
        )


@api.route('/api/azs')
def azs():
    '''
    ---
   get:
     summary: Данные АЗС
     parameters:
         - in: query
           name: azs
           schema:
             type: integer
             example: 1
           description: azs
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   id:
                     type: string
                   name:
                     type: string
                   addres:
                     type: string
                   petrols:
                     type: array
                     items:
                       type: object
                       properties:
                           price:
                             type: number
                           price:
                             type: array
                             items:
                               type: string
                   lat:
                     type: number
                   lon:
                     type: number
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
       - map
    '''
    try:
        azs = request.args.get('azs')
        if not azs:
            return current_app.response_class(
                response=json.dumps(
                    {'error': f'Не передан обязательный параметр'}
                ),
                status=400,
                mimetype='application/json'
            )
        return current_app.response_class(
            response=json.dumps(
                {
                    'id': azs,
                    'name': "АЗС \"САМБЕК\"",
                    'addres': "Таганрог, ул. Центральная, 20",
                    'petrols': [
                        {
                            'name': '95',
                            'price': 42.30
                        },
                        {
                            'name': '95',
                            'price': 42.30
                        },
                    ],
                    'services': ["wash", "market", "cafe"],
                    'lat': 47.433274431304454,
                    'lon': 38.931525186505986,
                }
            ),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return current_app.response_class(
            response=json.dumps(
                {'error': f'ERROR: {e}!'}
            ),
            status=400,
            mimetype='application/json'
        )
