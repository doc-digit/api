import requests


def test_file_get(client):
    resp = client.get("/storage/file/3fa85f64-5717-4562-b3fc-2c963f66afa6")
    print(resp.text)
    assert resp.status_code == 404

