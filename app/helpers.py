# -*- coding: utf-8 -*-
import requests
import json


def format_phone_number(phone_number):
    # Удаление всех символов, кроме цифр
    phone_number = ''.join(filter(str.isdigit, phone_number))

    # Проверка длины номера телефона
    if len(phone_number) != 11:
        return phone_number  # Возвращаем исходную строку, если длина некорректна

    # Форматирование номера телефона в виде "7-XXX-XXX-XX-XX"
    formatted_phone_number = f"7-{phone_number[1:4]}-{phone_number[4:7]}-{phone_number[7:9]}-{phone_number[9:11]}"

    return formatted_phone_number


def send_sms(phones, text, total_price=0):
    login = 'InfoDomDev'  # Логин в smsc
    password = 'yBEgupqPBrPK37Z'  # Пароль в smsc
    sender = 'Test'  # Имя отправителя
    # Возможные ошибки
    errors = {
        1: 'Ошибка в параметрах.',
        2: 'Неверный логин или пароль.',
        3: 'Недостаточно средств на счете Клиента.',
        4: 'IP-адрес временно заблокирован из-за частых ошибок в запросах. Подробнее',
        5: 'Неверный формат даты.',
        6: 'Сообщение запрещено (по тексту или по имени отправителя).',
        7: 'Неверный формат номера телефона.',
        8: 'Сообщение на указанный номер не может быть доставлено.',
        9: 'Отправка более одного одинакового запроса на передачу SMS-сообщения либо более пяти одинаковых запросов на получение стоимости сообщения в течение минуты. '
    }
    # Отправка запроса
    url = f"https://smsc.ru/sys/send.php?login={login}&psw={password}&phones={phones}&mes={text}&cost={total_price}&fmt=3&sender={sender}"
    answer = json.loads(requests.get(url).text)
    print(answer)
    if 'error_code' in answer:
        # Возникла ошибка
        return {
            'status': 'error',
            'response': errors[answer['error_code']],
        }
    else:
        if total_price == 1:
            # Не отправлять, узнать только цену
            print('Будут отправлены: %d SMS, цена рассылки: %s' % (answer['cnt'], answer['cost'].encode('utf-8')))
        else:
            # СМС отправлен, ответ сервера
            return {
                'status': 'ok',
                'response': answer,
            }


def get_user(phone):
    base_url = "http://94.79.22.45:8282/demoemitent/hs/cards"
    username = "mobile"
    password = "%#|AqLB{1f"
    organization_id = "612306662431"
    department_id = "mobile"

    # Создание заголовков авторизации
    auth = (username, password)
    request_data = {
        "organizationId": organization_id,
        "departmentId": department_id,
        "phone": format_phone_number(phone)
    }
    # Отправка POST-запроса
    response = requests.post(f"{base_url}/getClientInfo", json=request_data, auth=auth)
    if response.status_code != 200:
        return None
    else:
        return response.json()["data"]
