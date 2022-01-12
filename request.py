import requests
# response = requests.post("http://localhost:5000/pc/1", {"cpu": "i7", "ssd": "128", "ram": "8", "price": 1000})
# response = requests.post("http://localhost:5000/customer/1", {'name': 'Murad', 'surname': 'Abdullayev', 'email': 'example@gmail.com'})
# response = requests.get("http://localhost:5000/showclient/1")
# response = requests.post("http://localhost:5000/deals/1", {'pc_id': 1, 'customer_id': 1})
response = requests.get("http://localhost:5000/deals/1")
print(response.json())