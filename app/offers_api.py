# api.py
import json
from flask import Blueprint, request, current_app, url_for
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

api = Blueprint('offers_api', __name__)


@api.route('/api/all-offers')
def all_offers():
    '''
    ---
   get:
     summary: Все акции
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
                   offers:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: integer
                           dates:
                             type: string
                           title:
                             type: string
                           description:
                             type: string
                           full-description:
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
       - offers
    '''
    token = request.args.get('token')

    return current_app.response_class(
        response=json.dumps(
            {
                'offers': [
                    {
                        'id': 1,
                        'dates': 'c 22.04.2023 по 22.08.2023',
                        'title': 'Кофе в подарок',
                        'description': '6 чашка кофе в подарок',
                        'full-description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent purus purus, scelerisque id metus in, luctus porta leo. Mauris sapien sem, posuere vel feugiat sit amet, pellentesque sed lectus. Vestibulum dictum, urna ac egestas venenatis, tellus felis feugiat est, vitae eleifend sapien ipsum sed est. Curabitur massa metus, porttitor vel pellentesque ut, viverra non augue. Nulla sagittis a magna eu pharetra. Sed lacinia convallis justo, eu vestibulum sem iaculis finibus. In hac habitasse platea dictumst. Sed non diam eget libero posuere scelerisque. Nunc sed enim cursus, dictum sapien eget, lacinia sem. Fusce convallis feugiat ligula, id maximus neque ultricies sit amet. Proin orci velit, faucibus id lectus quis, molestie sodales urna. Pellentesque ac ante commodo, ullamcorper elit sit amet, ornare mi.'
                    },
                    {
                        'id': 2,
                        'dates': 'c 22.04.2023 по 22.08.2023',
                        'title': 'День мороженного',
                        'description': '6 чашка кофе в подарок',
                        'full-description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent purus purus, scelerisque id metus in, luctus porta leo. Mauris sapien sem, posuere vel feugiat sit amet, pellentesque sed lectus. Vestibulum dictum, urna ac egestas venenatis, tellus felis feugiat est, vitae eleifend sapien ipsum sed est. Curabitur massa metus, porttitor vel pellentesque ut, viverra non augue. Nulla sagittis a magna eu pharetra. Sed lacinia convallis justo, eu vestibulum sem iaculis finibus. In hac habitasse platea dictumst. Sed non diam eget libero posuere scelerisque. Nunc sed enim cursus, dictum sapien eget, lacinia sem. Fusce convallis feugiat ligula, id maximus neque ultricies sit amet. Proin orci velit, faucibus id lectus quis, molestie sodales urna. Pellentesque ac ante commodo, ullamcorper elit sit amet, ornare mi.'
                    },
                    {
                        'id': 3,
                        'dates': 'c 22.04.2023 по 22.08.2023',
                        'title': 'Плати бонусами',
                        'description': '6 чашка кофе в подарок',
                        'full-description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent purus purus, scelerisque id metus in, luctus porta leo. Mauris sapien sem, posuere vel feugiat sit amet, pellentesque sed lectus. Vestibulum dictum, urna ac egestas venenatis, tellus felis feugiat est, vitae eleifend sapien ipsum sed est. Curabitur massa metus, porttitor vel pellentesque ut, viverra non augue. Nulla sagittis a magna eu pharetra. Sed lacinia convallis justo, eu vestibulum sem iaculis finibus. In hac habitasse platea dictumst. Sed non diam eget libero posuere scelerisque. Nunc sed enim cursus, dictum sapien eget, lacinia sem. Fusce convallis feugiat ligula, id maximus neque ultricies sit amet. Proin orci velit, faucibus id lectus quis, molestie sodales urna. Pellentesque ac ante commodo, ullamcorper elit sit amet, ornare mi.'
                    }
                ],
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/personal-offers')
def personal_offers():
    '''
    ---
   get:
     summary: Персональные предложения
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
                   offers:
                     type: array
                     items:
                       type: object
                       properties:
                           id:
                             type: integer
                           dates:
                             type: string
                           title:
                             type: string
                           description:
                             type: string
                           full-description:
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
       - offers
    '''
    token = request.args.get('token')

    return current_app.response_class(
        response=json.dumps(
            {
                'offers': [
                    {
                        'id': 1,
                        'dates': 'c 22.04.2023 по 22.08.2023',
                        'title': 'Кофе в подарок',
                        'description': '6 чашка кофе в подарок',
                        'full-description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent purus purus, scelerisque id metus in, luctus porta leo. Mauris sapien sem, posuere vel feugiat sit amet, pellentesque sed lectus. Vestibulum dictum, urna ac egestas venenatis, tellus felis feugiat est, vitae eleifend sapien ipsum sed est. Curabitur massa metus, porttitor vel pellentesque ut, viverra non augue. Nulla sagittis a magna eu pharetra. Sed lacinia convallis justo, eu vestibulum sem iaculis finibus. In hac habitasse platea dictumst. Sed non diam eget libero posuere scelerisque. Nunc sed enim cursus, dictum sapien eget, lacinia sem. Fusce convallis feugiat ligula, id maximus neque ultricies sit amet. Proin orci velit, faucibus id lectus quis, molestie sodales urna. Pellentesque ac ante commodo, ullamcorper elit sit amet, ornare mi.'
                    },
                ],
            }
        ),
        status=200,
        mimetype='application/json'
    )


@api.route('/api/offer')
def offer():
    '''
    ---
   get:
     summary: Акция
     parameters:
         - in: query
           name: offer
           schema:
             type: integer
             example: 1
           description: offer
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
                   id:
                     type: integer
                   dates:
                     type: string
                   title:
                     type: string
                   description:
                     type: string
                   full-description:
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
       - offers
    '''
    token = request.args.get('token')
    offer = request.args.get('offer')

    return current_app.response_class(
        response=json.dumps(
            {

                'id': 1,
                'dates': 'c 22.04.2023 по 22.08.2023',
                'title': 'Кофе в подарок',
                'description': '6 чашка кофе в подарок',
                'full-description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent purus purus, scelerisque id metus in, luctus porta leo. Mauris sapien sem, posuere vel feugiat sit amet, pellentesque sed lectus. Vestibulum dictum, urna ac egestas venenatis, tellus felis feugiat est, vitae eleifend sapien ipsum sed est. Curabitur massa metus, porttitor vel pellentesque ut, viverra non augue. Nulla sagittis a magna eu pharetra. Sed lacinia convallis justo, eu vestibulum sem iaculis finibus. In hac habitasse platea dictumst. Sed non diam eget libero posuere scelerisque. Nunc sed enim cursus, dictum sapien eget, lacinia sem. Fusce convallis feugiat ligula, id maximus neque ultricies sit amet. Proin orci velit, faucibus id lectus quis, molestie sodales urna. Pellentesque ac ante commodo, ullamcorper elit sit amet, ornare mi.'
            }
        ),
        status=200,
        mimetype='application/json'
    )