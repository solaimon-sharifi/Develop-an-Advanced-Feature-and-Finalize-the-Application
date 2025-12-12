def create_user_payload(username: str):
    return {
        "username": username,
        "email": f"{username}@valorant.app",
        "password": "Str0ngPass!",
    }


def authenticate(client, username: str):
    client.post("/register", json=create_user_payload(username))
    response = client.post("/login", json={"username": username, "password": "Str0ngPass!"})
    assert response.status_code == 200
    return response.json()


def assert_redirects_to_login(response):
    assert response.status_code in (302, 303)
    location = response.headers.get("location")
    assert location is not None
    assert location.endswith("/login")


def test_register_and_login_flow(client):
    response = client.post("/register", json=create_user_payload("testcoach"))
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testcoach"
    assert data["email"].endswith("@valorant.app")

    login = client.post("/login", json={"username": "testcoach", "password": "Str0ngPass!"})
    assert login.status_code == 200
    payload = login.json()
    assert "access_token" in payload
    assert "refresh_token" in payload
    assert payload["username"] == "testcoach"
    assert payload["user_id"] > 0
    assert payload["token_type"] == "bearer"


def test_dashboard_html_redirects_without_auth(client):
    response = client.get("/dashboard/app", follow_redirects=False)
    assert_redirects_to_login(response)


def test_valorant_dashboard_html_redirects_without_auth(client):
    response = client.get("/valorant-dashboard", follow_redirects=False)
    assert_redirects_to_login(response)


def test_sessions_api_requires_auth(client):
    response = client.get("/sessions")
    assert response.status_code == 401


def test_dashboard_requires_jwt(client):
    response = client.get("/dashboard")
    assert response.status_code == 401
    assert response.json()["detail"].startswith("Not authenticated")


def test_create_and_list_matches(client):
    auth = authenticate(client, "matchcoach")
    headers = {"Authorization": f"Bearer {auth['access_token']}"}

    match_payload = {
        "map": "Ascent",
        "agent": "Jett",
        "score": 9,
        "notes": "Utility was on point",
    }
    post_resp = client.post("/matches", json=match_payload, headers=headers)
    assert post_resp.status_code == 201
    stored = post_resp.json()
    assert stored["map"] == "Ascent"
    assert stored["agent"] == "Jett"
    assert stored["score"] == 9

    list_resp = client.get("/matches", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["notes"] == "Utility was on point"
    assert items[0]["score"] == 9


def test_dashboard_returns_matches_and_strategies(client):
    auth = authenticate(client, "dashboardco")
    headers = {"Authorization": f"Bearer {auth['access_token']}"}

    client.post(
        "/matches",
        json={"map": "Bind", "agent": "Sage", "score": 7, "notes": "Heal rounds"},
        headers=headers,
    )
    client.post(
        "/strategies",
        json={"title": "Site Control", "description": "Slow push with wall lineups"},
        headers=headers,
    )

    dashboard = client.get("/dashboard", headers=headers)
    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert payload["user"]["username"] == "dashboardco"
    assert payload["matches"]
    assert payload["strategies"]
    assert payload["matches"][0]["map"] == "Bind"
    assert payload["strategies"][0]["title"] == "Site Control"



def test_create_and_list_sessions(client):
    auth = authenticate(client, "sessioncoach")
    headers = {"Authorization": f"Bearer {auth['access_token']}"}

    session_payload = {
        "title": "Recoil Clinic",
        "focus_area": "Jett Crosshots",
        "duration_minutes": 45,
        "notes": "Playback review with tracer input",
    }
    post_resp = client.post("/sessions", json=session_payload, headers=headers)
    assert post_resp.status_code == 201
    stored = post_resp.json()
    assert stored["title"] == "Recoil Clinic"
    assert stored["focus_area"] == "Jett Crosshots"
    assert stored["duration_minutes"] == 45

    list_resp = client.get("/sessions", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["notes"] == "Playback review with tracer input"