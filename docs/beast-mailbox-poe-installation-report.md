# Beast Mailbox – Poe Installation Report

## Summary
- Installed `beast-mailbox-core` on Poe (`pip install git+https://github.com/nkllon/beast-mailbox-core.git`)
- Started listener (`beast-mailbox-service poe --redis-host 192.168.1.119 --redis-password beastmode2025 --echo`)
- Sent test message (`beast-mailbox-send herbert poe --message "Live test message!"`) and confirmed receipt (`📬 poe <- herbert ...`)
- Created helper files for persistence (`/home/lou/start-mailbox-poe.sh`, `/tmp/beast-mailbox-poe.service`)

## Next Steps
- Install the unit file and enable the service via systemd, or run the starter script via nohup/tmux.
- Optional: publish the package to PyPI via `twine upload dist/*`.

