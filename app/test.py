'''import requests

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
                "phone": '7-952-600-05-36'
            }
response = requests.post(f"{base_url}/getClientInfo", json=request_data, auth=auth)
print(response.text)'''
import json
import pandas as pd
df = pd.read_json('carsBrands.json')
for i in df.values:
    print(i[0], i[2][0])
