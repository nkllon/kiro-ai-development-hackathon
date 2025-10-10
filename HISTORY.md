## Change Summary

- Created a standalone PyPI-ready package (`beast-mailbox-core`) for the Redis-backed mailbox, with CLI commands and documentation.
- Verified the package builds (wheel + sdist) and published it to a dedicated repo (`nkllon/beast-mailbox-core`).
- Added install instructions and operational notes referencing the new package.
- Successfully installed the mailbox service on Poe: listener running, test message received (`📬 poe <- herbert ...`).
- Delivered systemd/launch guidance so the mailbox can run persistently.
