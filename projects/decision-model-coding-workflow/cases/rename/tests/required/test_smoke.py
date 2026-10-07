"""Public smoke suite: one actor, happy paths only."""


def test_create_and_read(alice):
    record = alice.create("Smoke check", body="smoke body", tags=["smoke"])
    assert alice.get(f"/documents/{record['id']}").status_code == 200


def test_list_shows_created_document(alice):
    record = alice.create("Smoke check", body="smoke body")
    response = alice.get("/documents")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [record["id"]]


def test_update_body(alice):
    record = alice.create("Smoke check", body="smoke body")
    assert alice.patch(f"/documents/{record['id']}", json={"body": "updated body"}).status_code == 200


def test_exports_respond(alice):
    record = alice.create("Smoke check", body="smoke body")
    assert alice.get(f"/documents/{record['id']}/export").status_code == 200
    assert alice.get("/exports/documents").status_code == 200


def test_archive_then_restore(alice):
    record = alice.create("Smoke check", body="smoke body")
    archived = alice.post(f"/documents/{record['id']}/archive")
    assert archived.status_code == 200 and archived.json()["archived"] is True
    restored = alice.post(f"/documents/{record['id']}/restore")
    assert restored.status_code == 200 and restored.json()["archived"] is False


def test_delete(alice):
    record = alice.create("Smoke check", body="smoke body")
    assert alice.delete(f"/documents/{record['id']}").status_code == 204
    assert alice.get(f"/documents/{record['id']}").status_code == 404


def test_token_message_endpoint_responds(client):
    response = client.get("/token-message", params={"reason": "expired"})
    assert response.status_code == 200
    assert "message" in response.json()
