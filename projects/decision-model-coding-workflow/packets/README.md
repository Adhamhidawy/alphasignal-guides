# Saved packets from the scored run

Each file is the exact state and `next_check` question every picker received for one frozen Claude Code fix (run `main-001`, 2026-10-02). Replay one against a local or hosted decision model with `replay_packet.py`.

The reference column was prepared by the agent that ran the test, before any outcomes, and was not reviewed by a human. The choices are repetition 0, the predeclared primary repeat.

| Case | Task | Reference | Jev | winnow:e4b | Claude | Filename rule |
|---|---|---|---|---|---|---|
| I01 | Renaming a document looks successful in the PATCH response, but the next GET still shows the old title. Make a rename persist the same title the API returns. | integration | integration | integration | integration | targeted |
| I02 | Archiving or restoring a document shows the new state in the response, but the change is gone on the next request. Make archive and restore persist. | integration | integration | integration | integration | targeted |
| I03 | The document export lists documents in a different order than GET /documents, so paging through exports skips and repeats documents. Make exports follow the list endpoint's ordering and pagination. | integration | integration | integration | integration | targeted |
| I04 | Deleting a document leaves its tag rows behind in the database. Make deletion remove the document's tags too, leaving no orphaned rows. | integration | integration | integration | security | targeted |
| S01 | A user can update a document that belongs to someone else. Prevent users from updating another user's document. | security | security | security | security | targeted |
| S02 | The document list shows documents owned by other users. Make the list return only the requesting user's documents. | security | security | security | security | targeted |
| S03 | A user can export a document owned by another user. Prevent exporting another user's document. | security | security | security | security | targeted |
| S04 | A user can restore another user's archived document. Prevent users from restoring a document they do not own. | security | security | security | security | targeted |
| T01 | Titles with spaces around them are being rejected for length even when the visible title fits. Trim outer whitespace from a document title before enforcing its 80-character limit. | targeted | targeted | targeted | integration | targeted |
| T02 | A document can be created with a title made only of spaces. Reject titles that contain only whitespace. | targeted | targeted | targeted | targeted | targeted |
| T03 | Listing documents with limit=100 returns 422 even though the documented range is 1 to 100. Make the list accept the documented minimum and maximum limits. | targeted | targeted | targeted | integration | targeted |
| T04 | The expired-token message shows every word capitalized. Correct its capitalization so it reads as normal sentences. | targeted | targeted | targeted | targeted | security |
