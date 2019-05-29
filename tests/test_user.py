from api.models import User
from api.database import SessionLocal


def test_user_login(client):

    user = {"name": "test_user", "pin": 1234}
    u = User(**user)
    db_session = SessionLocal()
    db_session.add(u)
    db_session.commit()

    data = {"pin": 1234}
    resp = client.post("/user/login", json=data)
    print(resp.text)
    assert resp.status_code == 200

    resp_data = resp.json()
    assert user["name"] in resp_data["name"]
