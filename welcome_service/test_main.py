from http import client
from fastapi.testclient import TestClient
from .routers import image_welcome, welcome

client = TestClient(welcome)


def test_get_welcome():
    response = client.get(
        "/welcome/", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOiIxMDcxMmI5My00NzBkLTQzY2EtOGZlZi0zZmZiMzU5OGI5ZTMiLCJyb2xlIjoiQWRtaW4iLCJleHAiOjE2NDkyMzM4NzB9.2wK_zujYlP0bPiwCr95FM9MQNNjM11Ub-BongYlnFyg"})
    assert response.status_code == 200


# def test_get_all():
#     response = client.get("/user", json=data)
#     assert response.status_code == 200
#     assert data in response.json()


# def test_delete_users():
#     response = client.delete("/user/id")
#     assert response.status_code == 200
#     assert response.json() == {
#         "phone": "+9779844779207",
#         "password": "poojan12",
#     }
