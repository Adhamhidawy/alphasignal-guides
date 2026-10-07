from conftest import NOT_FOUND


def test_other_actor_cannot_rename(alice, bob, store):
    record = alice.create("Alice's")
    response = bob.patch(f"/documents/{record['id']}", json={"title": "Bob's now"})
    assert (response.status_code, response.json()) == (404, NOT_FOUND)
    assert store.document(record["id"])["title"] == "Alice's"


def test_rename_keeps_the_owner(alice, store):
    record = alice.create("Before")
    alice.patch(f"/documents/{record['id']}", json={"title": "After"})
    assert store.document(record["id"])["owner_id"] == "alice"


def test_renamed_document_stays_private(alice, bob):
    record = alice.create("Before")
    alice.patch(f"/documents/{record['id']}", json={"title": "After"})
    assert bob.get(f"/documents/{record['id']}").status_code == 404
    assert bob.get("/documents").json() == []
