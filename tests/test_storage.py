import requests


def test_upload_url(client):
    resp = client.get("/storage/upload")
    assert resp.status_code == 200
    resp_data = resp.json()
    assert "url" in resp_data


def test_file_get(client):
    resp = client.get("/storage/file/3fa85f64-5717-4562-b3fc-2c963f66afa6")
    print(resp.text)
    assert resp.status_code == 404


def test_upload_and_get(client):
    resp = client.get("/storage/upload")
    resp_data = resp.json()

    file_name = resp_data["id"]

    bin_data = b"A" * 10

    print(resp_data["url"])
    resp = requests.put(resp_data["url"], data=bin_data)
    print(resp.text, resp.request.method)
    assert resp.status_code == 200

    resp = client.get("/storage/file/" + file_name)
    resp_data = resp.json()

    assert resp_data["id"] == file_name

    resp = requests.get(resp_data["url"])

    assert resp.status_code == 200
    assert bin_data == resp.content
