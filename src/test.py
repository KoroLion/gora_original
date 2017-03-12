import requests

r_res = requests.post('http://127.0.0.1:8000/auth_api/', data={'login': 'KoroLion', 'password': '311923ARte'})
if r_res.status_code == 403:
    print('Incorrect login or password!')
else:
    print(r_res.text)
