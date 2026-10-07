def test_rename_response_has_the_trimmed_title(alice):
    record = alice.create("Before")
    response = alice.patch(f"/documents/{record['id']}", json={"title": "  Renamed  "})
    assert response.status_code == 200
    assert response.json()["title"] == "Renamed"


def test_rename_with_an_overlong_title_is_rejected(alice):
    record = alice.create("Before")
    assert alice.patch(f"/documents/{record['id']}", json={"title": "e" * 81}).status_code == 422


def test_body_only_update_keeps_the_title(alice):
    record = alice.create("Stable title", body="old")
    response = alice.patch(f"/documents/{record['id']}", json={"body": "new"})
    assert response.json()["title"] == "Stable title"


def test_owner_field_in_a_rename_request_is_ignored(alice):
    record = alice.create("Before")
    response = alice.patch(f"/documents/{record['id']}", json={"title": "After", "owner_id": "bob"})
    assert response.json()["owner_id"] == "alice"
