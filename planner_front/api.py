import requests

BASE_URL = "http://127.0.0.1:8000"

# OAuth2PasswordRequestForm을 이용해 데이터를 받기 때문에 application/x-www-form-urlencoded 형식으로 전송
def signin(email, password):
    response = requests.post(f"{BASE_URL}/users/signin", data={"username": email, "password": password})
    return response.json()

# 나머진 JSON 형식으로 전송
def signup(email, name, password):
    response = requests.post(f"{BASE_URL}/users/signup", json={"email": email, "name": name, "password": password})
    return response.json()

def get_events(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/event/", headers=headers)
    return response.json()

def get_event_detail(token, event_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/event/{event_id}", headers=headers)
    return response.json()

def add_event(token, event):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/event/", headers=headers, json=event)
    return response.json()

def update_event(token, event_id, event):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/event/{event_id}", headers=headers, json=event)
    return response.json()

def delete_event(token, event_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/event/{event_id}", headers=headers)
    return response.json()