from http import client
import re
from urllib import response
from fastapi.testclient import TestClient

from .routers import user

client = TestClient(user)

data = {
    "phone": "+9779844779207",
    "password": "poojan12",
}


def test_create_user():
    response = client.post("/user/", json=data)
    assert response.status_code == 200
    assert response.json() == data


def test_get_all():
    response = client.get("/user", json=data)
    assert response.status_code == 200
    assert data in response.json()


def test_delete_users():
    response = client.delete("/user/id")
    assert response.status_code == 200
    assert response.json() == {
        "phone": "+9779844779207",
        "password": "poojan12",
    }
