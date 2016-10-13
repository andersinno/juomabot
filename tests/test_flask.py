def test_flask_slash_ok(client, regular_products):
    resp = client.post('/slack', data={
        'user_name': 'akx',
        'text': 'coca-cola',
    })
    assert 'text/plain' in resp.headers['Content-Type']
    assert b'Added' in resp.data


def test_flask_slash_error(client, regular_products):
    resp = client.post('/slack', data={
        'user_name': 'akx',
        'text': 'florb',
    })
    assert 'text/plain' in resp.headers['Content-Type']
    assert resp.data.startswith(b':question:')
    assert b'find product' in resp.data
