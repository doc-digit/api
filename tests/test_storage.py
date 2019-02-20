import uuid 
import aiohttp

async def test_upload_url(test_cli):
    resp = await test_cli.get('/storage/upload')
    assert resp.status == 200
    resp_data = await resp.json()
    assert "url" in resp_data

async def test_file_get(test_cli):
    resp = await test_cli.get("/storage/file/abc")
    assert resp.status == 404

async def test_upload_and_get(test_cli):
    resp = await test_cli.get('/storage/upload')
    resp_data = await resp.json()
    
    file_name = resp_data['id']

    bin_data = b'A'*10
    async with aiohttp.ClientSession() as session:
        async with session.put(resp_data['url'],data=bin_data) as resp:
            assert resp.status == 200

    resp = await test_cli.get('/storage/file/'+file_name)
    resp_data = await resp.json()

    assert resp_data['id'] == file_name

    async with aiohttp.ClientSession() as session:
        async with session.get(resp_data['url']) as resp:
            assert resp.status == 200
            assert bin_data == await resp.read()