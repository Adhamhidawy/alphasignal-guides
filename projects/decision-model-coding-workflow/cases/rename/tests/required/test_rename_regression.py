def test_renamed_title_is_returned_by_the_next_read(alice):
    record = alice.create("Quarterly plan")
    renamed = alice.patch(f"/documents/{record['id']}", json={"title": "Quarterly plan v2"})
    assert renamed.json()["title"] == "Quarterly plan v2"
    assert alice.get(f"/documents/{record['id']}").json()["title"] == "Quarterly plan v2"
