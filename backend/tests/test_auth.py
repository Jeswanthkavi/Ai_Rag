def test_register_missing_data(client):

    response = client.post(
        "/auth/register",
        json={}
    )

    assert response.status_code in [
        400,
        422
    ]


def test_login_missing_data(client):

    response = client.post(
        "/auth/login",
        json={}
    )

    assert response.status_code in [
        400,
        401,
        422
    ]