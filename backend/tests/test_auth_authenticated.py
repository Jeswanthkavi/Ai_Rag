def test_login_success(
    client,
    test_user
):

    response = client.post(
        "/auth/login",
        json={
            "email":
                test_user["user"].email,

            "password":
                test_user["password"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data

    assert data["token_type"] == "bearer"


def test_get_current_user(
    authenticated_client,
    test_user
):

    response = authenticated_client.get(
        "/auth/me"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == (
        test_user["user"].email
    )

    assert data["name"] == "Test User"