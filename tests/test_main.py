
async def test_swagger(test_cli):
    resp = await test_cli.get('/swagger')
    assert resp.status == 200