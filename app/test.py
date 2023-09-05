import requests
import datetime, time

base_url = "http://80.72.17.245:8282/demoemitent/hs/cards"
username = "mobile"
password = "%#|AqLB{1f"
organization_id = "612306662431"
department_id = "mobile"

# Создание заголовков авторизации
auth = (username, password)
course = 47.8
amount = 100
request_data = {
        "requestId": f'814ea82a-6387-4587-9cdc-{int(time.time())}',
        "requestDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "organizationId": organization_id,
        "departmentId": department_id,
        'goodsId': '93',
        'price': 47.8,
        'amount': round(round(float(amount) / course) * course, 2),
        'quantity': round(float(amount) / course),
        'card': {
            'number': '000000000025',
            'id': '0B98BBC9C4064C5AA974A819060A5DFF'
        }
    }
print(request_data)
response = requests.post(f"{base_url}/buyfuel", json=request_data, auth=auth)
print(response.text)
