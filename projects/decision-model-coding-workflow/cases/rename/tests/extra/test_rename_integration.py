def test_patch_response_matches_the_next_read(alice):
    record = alice.create("Before", tags=["a"])
    response = alice.patch(
        f"/documents/{record['id']}", json={"title": "  Mixed  case  ", "tags": ["a", "a", "b"]}
    )
    assert response.json() == alice.get(f"/documents/{record['id']}").json()


def test_rename_appears_in_list_and_export(alice):
    record = alice.create("Before")
    alice.patch(f"/documents/{record['id']}", json={"title": "Listed name"})
    assert alice.get("/documents").json()[0]["title"] == "Listed name"
    assert alice.get("/exports/documents").json()["documents"][0]["title"] == "Listed name"


def test_rename_is_written_to_the_documents_table(alice, store):
    record = alice.create("Before")
    alice.patch(f"/documents/{record['id']}", json={"title": "Stored name"})
    assert store.document(record["id"])["title"] == "Stored name"


def test_two_consecutive_renames_keep_the_last(alice):
    record = alice.create("First")
    alice.patch(f"/documents/{record['id']}", json={"title": "Second"})
    alice.patch(f"/documents/{record['id']}", json={"title": "Third"})
    assert alice.get(f"/documents/{record['id']}").json()["title"] == "Third"
