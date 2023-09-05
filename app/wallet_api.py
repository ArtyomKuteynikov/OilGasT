# api.py
import json
from flask import Blueprint, request, current_app, url_for
from werkzeug.security import generate_password_hash
import base64
from PIL import Image
from io import BytesIO
from . import db
from .helpers import get_user
from .models import User, Codes
from iqsms_rest import Gate
import random
import time
from .config import *
from os import getcwd
import uuid
import requests
import datetime
from .static_dicts import *


def format_phone_number(phone_number):
    # Удаление всех символов, кроме цифр
    phone_number = ''.join(filter(str.isdigit, phone_number))

    # Проверка длины номера телефона
    if len(phone_number) != 11:
        return phone_number  # Возвращаем исходную строку, если длина некорректна

    # Форматирование номера телефона в виде "7-XXX-XXX-XX-XX"
    formatted_phone_number = f"7-{phone_number[1:4]}-{phone_number[4:7]}-{phone_number[7:9]}-{phone_number[9:11]}"

    return formatted_phone_number


idempotence_key = str(uuid.uuid4())

api = Blueprint('wallet_api', __name__)


@api.route('/api/my-balance')
def my_balance():
    '''
    ---
   get:
     summary: Баланс
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
                   points:
                     type: integer
                   deposit:
                     type: integer
                   available_points:
                     type: integer
                   available_deposit:
                     type: integer
                   coffee:
                     type: integer
                   burger:
                     type: integer
                   hot-dog:
                     type: integer
                   liters:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: integer
                           name:
                             type: string
                           amount:
                             type: integer
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
       - wallet
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
    phone = format_phone_number(user.phone)
    # Установка параметров для тестирования
    base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
    username = "mobile"
    password = "%#|AqLB{1f"
    organization_id = "612306662431"
    department_id = "mobile"

    # Создание заголовков авторизации
    auth = (username, password)

    # Создание JSON-запроса
    request_data = {
        "organizationId": organization_id,
        "departmentId": department_id,
        "phone": phone
    }

    # Отправка POST-запроса
    response = requests.post(f"{base_url}/getClientInfo", json=request_data, auth=auth)
    if response.status_code == 200:
        # Получение JSON-данных из ответа
        response_data = response.json()

        # Обработка полученных данных
        result_code = response_data["result"]["code"]
        result_description = response_data["result"]["description"]
        client_info = response_data["data"]["client"]
        cards_info = response_data["data"]["cards"][0]
        points = cards_info["points"]
        money = cards_info["money"]
        liters = []
        for i in cards_info["liters"]:
            liters.append({
                'id': i['goodsId'],
                'name': goods[i["goodsId"]] if i["goodsId"] in goods else '',
                'amount': i['quantity']
            })
    else:
        points = 0
        money = 0
        liters = []

    return current_app.response_class(
        response=json.dumps(
            {
                'points': points,
                'available_points': points,
                'available_deposit': money,
                'deposit': money,
                'coffee': 0,
                'burger': 0,
                'hot-dog': 0,
                'liters': liters,
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/my-liters')
def my_liters():
    '''
    ---
   get:
     summary: Литры
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
                   liters:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: integer
                           name:
                             type: string
                           amount:
                             type: integer
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
       - wallet
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
    phone = format_phone_number(user.phone)
    # Установка параметров для тестирования
    base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
    username = "mobile"
    password = "%#|AqLB{1f"
    organization_id = "612306662431"
    department_id = "mobile"

    # Создание заголовков авторизации
    auth = (username, password)

    # Создание JSON-запроса
    request_data = {
        "organizationId": organization_id,
        "departmentId": department_id,
        "phone": phone
    }

    # Отправка POST-запроса
    response = requests.post(f"{base_url}/getClientInfo", json=request_data, auth=auth)
    if response.status_code == 200:
        # Получение JSON-данных из ответа
        response_data = response.json()

        # Обработка полученных данных
        result_code = response_data["result"]["code"]
        result_description = response_data["result"]["description"]
        client_info = response_data["data"]["client"]
        cards_info = response_data["data"]["cards"][0]
        points = cards_info["points"]
        money = cards_info["money"]
        liters = []
        for i in cards_info["liters"]:
            liters.append({
                'id': i['goodsId'],
                'name': goods[i["goodsId"]] if i["goodsId"] in goods else '',
                'amount': i['quantity']
            })
    else:
        points = 0
        money = 0
        liters = []

    return current_app.response_class(
        response=json.dumps(
            {
                'liters': liters,
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/exchange')
def exchange():
    '''
    ---
   get:
     summary: Обменять
     parameters:
         - in: query
           name: amount
           schema:
             type: integer
             example: 10
           description: amount
         - in: query
           name: from
           schema:
             type: string
             example: points
           description: from
         - in: query
           name: to
           schema:
             type: string
             example: money
           description: to
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
                   points:
                     type: integer
                   deposit:
                     type: integer
                   available_points:
                     type: integer
                   available_deposit:
                     type: integer
                   coffee:
                     type: integer
                   burger:
                     type: integer
                   hot-dog:
                     type: integer
                   liters:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: integer
                           name:
                             type: string
                           amount:
                             type: integer
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
       '402':
         description: Недостаточно средств
         content:
           application/json:
             schema: ErrorSchema
     tags:
       - wallet
    '''
    try:
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
        from_ = request.args.get('from')
        to_ = request.args.get('to')
        amount = request.args.get('amount')
        base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
        username = "mobile"
        password = "%#|AqLB{1f"
        organization_id = "612306662431"
        department_id = "mobile"

        # Создание заголовков авторизации
        auth = (username, password)
        request_data = {
            "organizationId": organization_id,
            "departmentId": department_id,
            "phone": format_phone_number(user.phone)
        }
        # Отправка POST-запроса
        response = requests.post(f"{base_url}/getClientInfo", json=request_data, auth=auth)
        if response.status_code != 200:
            return current_app.response_class(
                response=json.dumps(
                    {'error': f'USER DOES NOT EXIST'}
                ),
                status=403,
                mimetype='application/json'
            )
        # Получение JSON-данных из ответа
        response_data = response.json()
        cards_info = response_data["data"]["cards"][0]

        # Создание JSON-запроса
        request_data = {
            "organizationId": organization_id,
            "departmentId": department_id,
        }
        # Отправка POST-запроса
        if to_ == 'money':
            response = requests.post(f"{base_url}/moneyCourse", json=request_data, auth=auth)
            if response.status_code == 200:
                # Получение JSON-данных из ответа
                response_data = response.json()
                course = float(response_data['data']['course'])
                print(course)
                request_data = {
                    "requestId": int(time.time()),
                    "requestDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "organizationId": organization_id,
                    "departmentId": department_id,
                    'course': course,
                    'points': amount,
                    'money': float(amount) // course,
                    'card': {
                        'number': cards_info['number'],
                        'id': cards_info['id']
                    }
                }
                print(request_data)

                # Отправка POST-запроса
                response = requests.post(f"{base_url}/convertPointsToMoney", json=request_data, auth=auth)
                print(response.text)
                if response.status_code == 200:
                    pass
                else:
                    return current_app.response_class(
                        response=json.dumps(
                            {'error': f'ERROR: Ошибка стороннего сервера!'}
                        ),
                        status=400,
                        mimetype='application/json'
                    )
            else:
                return current_app.response_class(
                    response=json.dumps(
                        {'error': f'ERROR: Ошибка стороннего сервера!'}
                    ),
                    status=400,
                    mimetype='application/json'
                )
        elif from_ == 'money':
            request_data = {
                "organizationId": organization_id,
                "departmentId": department_id,
                'goodsId': to_
            }
            response = requests.post(f"{base_url}/fuelPrice", json=request_data, auth=auth)
            if response.status_code == 200:
                # Получение JSON-данных из ответа
                response_data = response.json()
                course = float(response_data['data']['price'])
                print(course)
                request_data = {
                    "requestId": f'814ea82a-6387-4587-9cdc-{int(time.time())}',
                    "requestDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "organizationId": organization_id,
                    "departmentId": department_id,
                    'goodsId': to_,
                    'price': course,
                    'amount': int((float(amount) / course)*100)/100 * course,
                    'quantity': int((float(amount) / course)*100)/100,
                    'card': {
                        'number': cards_info['number'],
                        'id': cards_info['id']
                    }
                }
                if float(amount) // course < 1:
                    return current_app.response_class(
                        response=json.dumps(
                            {'error': f'ERROR: MINIMUM AMOUNT IS {course}!'}
                        ),
                        status=400,
                        mimetype='application/json'
                    )
                print(request_data)
                # Отправка POST-запроса
                response = requests.post(f"{base_url}/buyfuel", json=request_data, auth=auth)
                print(response.text)
                if response.status_code == 200:
                    pass
                else:
                    print(response.text)
                    return current_app.response_class(
                        response=json.dumps(
                            {'error': f'ERROR: Ошибка стороннего сервера!'}
                        ),
                        status=400,
                        mimetype='application/json'
                    )
            else:
                return current_app.response_class(
                    response=json.dumps(
                        {'error': f'ERROR: Ошибка стороннего сервера!'}
                    ),
                    status=400,
                    mimetype='application/json'
                )
        else:
            print(123)
            request_data = {
                "organizationId": organization_id,
                "departmentId": department_id,
                'goodsId': to_
            }
            response = requests.post(f"{base_url}/fuelCourse", json=request_data, auth=auth)
            print(response.text)
            if response.status_code == 200:
                # Получение JSON-данных из ответа
                response_data = response.json()
                course = float(response_data['data']['course'])
                print(course)
                request_data = {
                    "requestId": int(time.time()),
                    "requestDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "organizationId": organization_id,
                    "departmentId": department_id,
                    'goodsId': to_,
                    'course': course,
                    'points': (float(amount) // course) * course,
                    'quantity': float(amount) // course,
                    'card': {
                        'number': cards_info['number'],
                        'id': cards_info['id']
                    }
                }
                if float(amount) // course < 1:
                    return current_app.response_class(
                        response=json.dumps(
                            {'error': f'ERROR: MINIMUM AMOUNT IS {course}!'}
                        ),
                        status=400,
                        mimetype='application/json'
                    )
                print(request_data)
                # Отправка POST-запроса
                response = requests.post(f"{base_url}/convertPointsToFuel", json=request_data, auth=auth)
                print(response.text)
                if response.status_code == 200:
                    pass
                else:
                    print(response.text)
                    return current_app.response_class(
                        response=json.dumps(
                            {'error': f'ERROR: Ошибка стороннего сервера!'}
                        ),
                        status=400,
                        mimetype='application/json'
                    )
            else:
                return current_app.response_class(
                    response=json.dumps(
                        {'error': f'ERROR: Ошибка стороннего сервера!'}
                    ),
                    status=400,
                    mimetype='application/json'
                )
        # Отправка POST-запроса
        if response.status_code == 200:
            print(response.text)
            # Получение JSON-данных из ответа
            response_data = response.json()
            cards_info = response_data["data"]["cards"][0]
            points = cards_info["points"]
            money = cards_info["money"]
            liters = []
            for i in cards_info["liters"]:
                liters.append({
                    'id': i['goodsId'],
                    'name': goods[i["goodsId"]] if i["goodsId"] in goods else '',
                    'amount': i['quantity']
                })
        else:
            points = 0
            money = 0
            liters = []
        return current_app.response_class(
            response=json.dumps(
                {
                    'points': points,
                    'available_points': points,
                    'available_deposit': money,
                    'deposit': money,
                    'coffee': 0,
                    'burger': 0,
                    'hot-dog': 0,
                    'liters': liters,
                }
            ),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(e)
        return current_app.response_class(
            response=json.dumps(
                {'error': f'ERROR: {e}!'}
            ),
            status=400,
            mimetype='application/json'
        )


@api.route('/api/money-course')
def money_course():
    '''
    ---
   get:
     summary: Курс обмена баллов на деньги
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
                   course:
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
       - wallet
    '''
    base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
    username = "mobile"
    password = "%#|AqLB{1f"
    organization_id = "612306662431"
    department_id = "mobile"

    # Создание заголовков авторизации
    auth = (username, password)
    request_data = {
        "organizationId": organization_id,
        "departmentId": department_id,
    }
    # Отправка POST-запроса
    response = requests.post(f"{base_url}/moneyCourse", json=request_data, auth=auth)
    if response.status_code == 200:
        # Получение JSON-данных из ответа
        response_data = response.json()
        course = float(response_data['data']['course'])
        return current_app.response_class(
            response=json.dumps(
                {'course': course}
            ),
            status=200,
            mimetype='application/json'
        )
    else:
        return current_app.response_class(
            response=json.dumps(
                {'error': f'ERROR: 1C ERROR!'}
            ),
            status=400,
            mimetype='application/json'
        )


@api.route('/api/fuel-course')
def fuel_course():
    '''
    ---
   get:
     summary: Курс обмена баллов на литры
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: xv2ossY6V9fikmjp$a45f9c93467deca882d3219ba4c568e3a9ebe4a53dbd17b03ec6987a9976b8bc
           description: token
         - in: query
           name: goodsId
           schema:
             type: string
             example: 95
           description: goodsId
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   course:
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
       - wallet
    '''
    goodsId = request.args.get('goodsId')
    base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
    username = "mobile"
    password = "%#|AqLB{1f"
    organization_id = "612306662431"
    department_id = "mobile"

    # Создание заголовков авторизации
    auth = (username, password)
    request_data = {
        "organizationId": organization_id,
        "departmentId": department_id,
        'goodsId': goodsId
    }
    response = requests.post(f"{base_url}/fuelCourse", json=request_data, auth=auth)
    if response.status_code == 200:
        # Получение JSON-данных из ответа
        response_data = response.json()
        print(response_data, request_data)
        course = float(response_data['data']['course'])
        return current_app.response_class(
            response=json.dumps(
                {'course': course}
            ),
            status=200,
            mimetype='application/json'
        )
    else:
        return current_app.response_class(
            response=json.dumps(
                {'error': f'ERROR: 1C ERROR!'}
            ),
            status=400,
            mimetype='application/json'
        )


@api.route('/api/share-liters')
def share_liters():
    '''
    ---
   get:
     summary: Поделиться литрами
     parameters:
         - in: query
           name: recipient
           schema:
             type: integer
             example: 79526000536
           description: recipient
         - in: query
           name: amount
           schema:
             type: string
             example: 1
           description: amount
         - in: query
           name: petrol
           schema:
             type: integer
             example: 95
           description: petrol
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
                   status:
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
       - wallet
    '''
    try:
        token = request.args.get('token')
        recipient = request.args.get('recipient')
        petrol = request.args.get('petrol')
        amount = request.args.get('amount')
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
        user1 = get_user(user.phone)
        if not user1:
            return current_app.response_class(
                response=json.dumps(
                    {'error': f'USER DOES NOT EXIST'}
                ),
                status=403,
                mimetype='application/json'
            )
        user2 = get_user(recipient)
        if not user2:
            return current_app.response_class(
                response=json.dumps(
                    {'error': f'RECIPIENT DOES NOT EXIST'}
                ),
                status=405,
                mimetype='application/json'
            )
        base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
        username = "mobile"
        password = "%#|AqLB{1f"
        organization_id = "612306662431"
        department_id = "mobile"

        # Создание заголовков авторизации
        auth = (username, password)

        # Создание JSON-запроса
        request_data = {
            "requestId": f'814ea82a-6387-4587-9cdc-{int(time.time())}',
            "requestDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "organizationId": organization_id,
            "departmentId": department_id,
            "goodsId": petrol,
            "quantity": amount,
            "card": {
                "number": user1['cards'][0]['number'],
                "id": user1['cards'][0]['id']
            },
            "card_consignee": {
                "number": user2['cards'][0]['number'],
                "id": user2['cards'][0]['id']
            }
        }

        # Установка заголовков контента
        headers = {
            "Content-Type": "application/json"
        }

        # Отправка POST-запроса
        response = requests.post(f"{base_url}/movefuel", json=request_data, auth=auth, headers=headers)
        if response.status_code != 200:
            return current_app.response_class(
                response=json.dumps(
                    {
                        'error': 'Не передан обязательный параметр или ошибка в параметрах'
                    }
                ),
                status=400,
                mimetype='application/json'
            )
        return current_app.response_class(
            response=json.dumps(
                {
                    'status': 'ok',
                }
            ),
            status=200,
            mimetype='application/json'
        )
    except:
        return current_app.response_class(
            response=json.dumps(
                {
                    'error': 'Не передан обязательный параметр или ошибка в параметрах'
                }
            ),
            status=400,
            mimetype='application/json'
        )


@api.route('/api/share-points')
def share_points():
    '''
    ---
   get:
     summary: Поделиться баллами
     parameters:
         - in: query
           name: recipient
           schema:
             type: integer
             example: 79526000536
           description: recipient
         - in: query
           name: amount
           schema:
             type: string
             example: 1
           description: amount
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
                   status:
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
       - wallet
    '''
    try:
        token = request.args.get('token')
        recipient = request.args.get('recipient')
        amount = request.args.get('amount')
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
        user1 = get_user(user.phone)
        if not user1:
            return current_app.response_class(
                response=json.dumps(
                    {'error': f'USER DOES NOT EXIST'}
                ),
                status=403,
                mimetype='application/json'
            )
        user2 = get_user(recipient)
        if not user2:
            return current_app.response_class(
                response=json.dumps(
                    {'error': f'RECIPIENT DOES NOT EXIST'}
                ),
                status=405,
                mimetype='application/json'
            )
        base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
        username = "mobile"
        password = "%#|AqLB{1f"
        organization_id = "612306662431"
        department_id = "mobile"

        # Создание заголовков авторизации
        auth = (username, password)

        # Создание JSON-запроса
        request_data = {
            "requestId": f'814ea82a-6387-4587-9cdc-{int(time.time())}',
            "requestDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "organizationId": organization_id,
            "departmentId": department_id,
            "points": amount,
            "card": {
                "number": user1['cards'][0]['number'],
                "id": user1['cards'][0]['id']
            },
            "card_consignee": {
                "number": user2['cards'][0]['number'],
                "id": user2['cards'][0]['id']
            }
        }

        # Установка заголовков контента
        headers = {
            "Content-Type": "application/json"
        }

        # Отправка POST-запроса
        response = requests.post(f"{base_url}/movepoints", json=request_data, auth=auth, headers=headers)
        if response.status_code != 200:
            return current_app.response_class(
                response=json.dumps(
                    {
                        'error': 'Не передан обязательный параметр или ошибка в параметрах'
                    }
                ),
                status=400,
                mimetype='application/json'
            )
        return current_app.response_class(
            response=json.dumps(
                {
                    'status': 'ok',
                }
            ),
            status=200,
            mimetype='application/json'
        )
    except:
        return current_app.response_class(
            response=json.dumps(
                {
                    'error': 'Не передан обязательный параметр или ошибка в параметрах'
                }
            ),
            status=400,
            mimetype='application/json'
        )


@api.route('/api/history')
def history():
    '''
    ---
   get:
     summary: История транзакций
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: OPMrexrW7r9vdO0D$36e5126f0fe9fa66bd278c8c25dd3ad319179a0edf5de678f58a95a0042b343d
           description: token
         - in: query
           name: startDate
           schema:
             type: string
             example: "2023-03-24T10:40:00"
           description: startDate
         - in: query
           name: endDate
           schema:
             type: string
             example: "2023-04-24T10:40:00"
           description: endDate
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   transactions:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: string
                           date:
                             type: string
                           departmentId:
                             type: string
                           goodsId:
                             type: string
                           paymentId:
                             type: string
                           quantity:
                             type: number
                           addPoints:
                             type: integer
                           writeoffPoints:
                             type: integer
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
       - wallet
    '''
    token = request.args.get('token')
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
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
    base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
    username = "mobile"
    password = "%#|AqLB{1f"
    organization_id = "612306662431"
    department_id = "mobile"

    # Создание заголовков авторизации
    auth = (username, password)

    # Создание JSON-запроса
    request_data = {
        "organizationId": organization_id,
        "departmentId": department_id,
        "phone": format_phone_number(user.phone),
        "period": {
            "startDate": startDate,
            "endDate": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        }
    }

    # Установка заголовков контента
    headers = {
        "Content-Type": "application/json"
    }

    # Отправка POST-запроса
    response = requests.post(f"{base_url}/getTransaction", json=request_data, auth=auth, headers=headers)
    if response.status_code == 200:
        # Получение JSON-данных из ответа
        transactions = []
        response_data = response.json()
        for i in response_data['data']['cards'][0]['transactions']:
            transactions.append({
                "id": i["id"],
                "date": '.'.join("2023-05-31T15:47:49".split('T')[0].split("-")[::-1]) + ' ' + ':'.join(
                    "2023-05-31T15:47:49".split('T')[1].split(":")[0:2]),
                "departmentId": departments[i["departmentId"]] if i["departmentId"] in departments else '',
                "goodsId": goods[i["goodsId"]] if i["goodsId"] in goods else '',
                "paymentId": payments[i["paymentId"]] if i["paymentId"] in payments else '',
                "quantity": i["quantity"],
                "addPoints": i["addPoints"],
                "writeoffPoints": i["writeoffPoints"]
            })

        return current_app.response_class(
            response=json.dumps(
                {
                    'transactions': transactions
                }
            ),
            status=200,
            mimetype='application/json'
        )
    else:
        return current_app.response_class(
            response=json.dumps(
                {
                    'error': 'Не передан обязательный параметр или ошибка в параметрах'
                }
            ),
            status=400,
            mimetype='application/json'
        )


@api.route('/api/promocode')
def promocode():
    '''
    ---
   get:
     summary: Применить промокод
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: OPMrexrW7r9vdO0D$36e5126f0fe9fa66bd278c8c25dd3ad319179a0edf5de678f58a95a0042b343d
           description: token
         - in: query
           name: promocode
           schema:
             type: string
             example: ТЕСТ2023
           description: promocode
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   status:
                     type: bool
                   data:
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
       - wallet
    '''
    token = request.args.get('token')
    promocode = request.args.get('promocode')
    return current_app.response_class(
        response=json.dumps(
            {
                'status': False,
                'data': 'Такого промокода не существует'
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/goods')
def goods_def():
    '''
    ---
   get:
     summary: Товары
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
                   goods:
                     type: array
                     items:
                       type: object
                       properties:
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
       - wallet
    '''
    goods_ = []
    for i in goods:
        goods_.append({'id': i, 'name': goods[i]})
    return {
        'goods': goods_
    }


@api.route('/api/add-money')
def add_money():
    '''
    ---
   get:
     summary: Пополнить
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: xv2ossY6V9fikmjp$a45f9c93467deca882d3219ba4c568e3a9ebe4a53dbd17b03ec6987a9976b8bc
           description: token
         - in: query
           name: amount
           schema:
             type: integer
             example: 1000
           description: amount
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   confirmation_url:
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
       - wallet
    '''
    token = request.args.get('token')
    user = User.query.filter_by(token=token).first()
    amount = request.args.get('amount')
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
    phone = format_phone_number(user.phone)
    # Установка параметров для тестирования
    base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
    username = "mobile"
    password = "%#|AqLB{1f"
    organization_id = "612306662431"
    department_id = "mobile"

    # Создание заголовков авторизации
    auth = (username, password)

    # Создание JSON-запроса
    request_data = {
        "requestId": int(time.time()),
        "requestDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "organizationId": organization_id,
        "departmentId": department_id,
        "phone": phone
    }

    # Отправка POST-запроса
    response = requests.post(f"{base_url}/getClientInfo", json=request_data, auth=auth)
    print(response.text)
    if response.status_code == 200:
        # Получение JSON-данных из ответа
        response_data = response.json()

        # Обработка полученных данных
        result_code = response_data["result"]["code"]
        result_description = response_data["result"]["description"]
        client_info = response_data["data"]["client"]
        cards_info = response_data["data"]["cards"][0]
        base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
        username = "mobile"
        password = "%#|AqLB{1f"
        organization_id = "612306662431"
        department_id = "mobile"

        # Создание заголовков авторизации
        auth = (username, password)

        # Создание JSON-запроса
        request_data = {
            "requestId": int(time.time()),
            "requestDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "organizationId": organization_id,
            "departmentId": department_id,
            "amount": amount,
            "card": {
                'number': cards_info['number'],
                'id': cards_info['id']
            }
        }

        # Отправка POST-запроса
        response = requests.post(f"{base_url}/addmoney", json=request_data, auth=auth)
        print(response.text)
        if response.status_code == 200:
            return current_app.response_class(
                response=json.dumps(
                    {
                        'confirmation_url': response.json()['data']['confirmation_url']
                    }
                ),
                status=200,
                mimetype='application/json'
            )
        else:
            try:
                description = response.json()["result"]["description"]
            except:
                description = 'Не передан обязательный пареметр или ошибка в параметрах'
    else:
        try:
            description = response.json()["result"]["description"]
        except:
            description = 'Не передан обязательный пареметр или ошибка в параметрах'
    return current_app.response_class(
        response=json.dumps(
            {
                'error': description
            }
        ),
        status=400,
        mimetype='application/json'
    )


@api.route('/api/buy-liters')
def buy_liters():
    '''
   ---
   get:
     summary: Купить литры
     parameters:
         - in: query
           name: token
           schema:
             type: string
             example: oYq4YOgZT996KQdD$a2e4161471c69eb3f29c7fea84fa050b8778143a96842f7629548d189276bb43
           description: token
         - in: query
           name: amount
           schema:
             type: integer
             example: 1
           description: amount
         - in: query
           name: goodsId
           schema:
             type: string
             example: 95
           description: goodsId
     responses:
       '200':
         description: Результат
         content:
           application/json:
             schema:      # Request body contents
               type: object
               properties:
                   points:
                     type: integer
                   available_points:
                     type: integer
                   available_deposit:
                     type: integer
                   deposit:
                     type: integer
                   coffee:
                     type: integer
                   burger:
                     type: integer
                   hot-dog:
                     type: integer
                   liters:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: string
                           name:
                             type: string
                           amount:
                             type: integer
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
       - wallet
    '''
    try:
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
        goodsId = request.args.get('goodsId')
        amount = request.args.get('amount')
        base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
        username = "mobile"
        password = "%#|AqLB{1f"
        organization_id = "612306662431"
        department_id = "mobile"

        # Создание заголовков авторизации
        auth = (username, password)
        request_data = {
            "organizationId": organization_id,
            "departmentId": department_id,
            "phone": format_phone_number(user.phone)
        }
        # Отправка POST-запроса
        response = requests.post(f"{base_url}/getClientInfo", json=request_data, auth=auth)
        if response.status_code != 200:
            return current_app.response_class(
                response=json.dumps(
                    {'error': f'USER DOES NOT EXIST'}
                ),
                status=403,
                mimetype='application/json'
            )
        # Получение JSON-данных из ответа
        response_data = response.json()
        cards_info = response_data["data"]["cards"][0]

        # Создание JSON-запроса
        request_data = {
            "organizationId": organization_id,
            "departmentId": department_id,
        }
        # Отправка POST-запроса
        request_data = {
            "organizationId": organization_id,
            "departmentId": department_id,
            'goodsId': goodsId
        }
        response = requests.post(f"{base_url}/fuelPrice", json=request_data, auth=auth)
        if response.status_code == 200:
            # Получение JSON-данных из ответа
            response_data = response.json()
            course = float(response_data['data']['price'])
            print(course)
            request_data = {
                "requestId": f'814ea82a-6387-4587-9cdc-{int(time.time())}',
                "requestDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "organizationId": organization_id,
                "departmentId": department_id,
                'goodsId': goodsId,
                'price': course,
                'amount': round(float(amount) * course, 2),
                'quantity': float(amount),
                'card': {
                    'number': cards_info['number'],
                    'id': cards_info['id']
                }
            }
            if float(amount) < 1:
                return current_app.response_class(
                    response=json.dumps(
                        {'error': f'ERROR: MINIMUM AMOUNT IS 1!'}
                    ),
                    status=400,
                    mimetype='application/json'
                )
            # Отправка POST-запроса
            response = requests.post(f"{base_url}/buyfuel", json=request_data, auth=auth)
            print(request_data)
            if response.status_code == 200:
                pass
            elif 'result' in response.json():
                print(response.text)
                return current_app.response_class(
                    response=json.dumps(
                        {'error': response.json()['result']['description']}
                    ),
                    status=400,
                    mimetype='application/json'
                )
            else:
                print(response.status_code)
                return current_app.response_class(
                    response=json.dumps(
                        {'error': f'ERROR: Ошибка стороннего сервера!'}
                    ),
                    status=400,
                    mimetype='application/json'
                )
        else:
            return current_app.response_class(
                response=json.dumps(
                    {'error': f'ERROR: Ошибка стороннего сервера!'}
                ),
                status=400,
                mimetype='application/json'
            )
        # Отправка POST-запроса
        if response.status_code == 200:
            print(response.text)
            # Получение JSON-данных из ответа
            response_data = response.json()
            cards_info = response_data["data"]["cards"][0]
            points = cards_info["points"]
            money = cards_info["money"]
            liters = []
            for i in cards_info["liters"]:
                liters.append({
                    'id': i['goodsId'],
                    'name': goods[i["goodsId"]] if i["goodsId"] in goods else '',
                    'amount': i['quantity']
                })
        else:
            points = 0
            money = 0
            liters = []
        return current_app.response_class(
            response=json.dumps(
                {
                    'points': points,
                    'available_points': points,
                    'available_deposit': money,
                    'deposit': money,
                    'coffee': 0,
                    'burger': 0,
                    'hot-dog': 0,
                    'liters': liters,
                }
            ),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(e)
        return current_app.response_class(
            response=json.dumps(
                {'error': f'ERROR: {e}!'}
            ),
            status=400,
            mimetype='application/json'
        )
