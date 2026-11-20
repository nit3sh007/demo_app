# Acme shop (demo app)

Small Flask shop with seeded bugs. It reports runtime errors to an outbox (`/_autofix/errors`, token protected) that the
separate bug-agent dashboard pulls. This repo is what Render deploys; it has no agent code and no secrets.

Pages: `/` (sign in, coupon, cart summary), `/checkout`, `/profile`, `/catalog`. Each has a seeded bug.
The branch tag `buggy-baseline` marks the buggy state the dashboard's Reset demo restores. After adding pages or bugs
run `git tag -f buggy-baseline`, then `git push` and `git push -f origin buggy-baseline`.

    pip install -r requirements.txt
    python webapp.py                      # http://127.0.0.1:5001
    pytest

Render: Build `pip install -r requirements.txt`, Start `gunicorn webapp:app --workers 1 --threads 4 --bind 0.0.0.0:$PORT`,
Health check `/healthz`, env var `AUTOFIX_TOKEN`. Keep one worker (the outbox is in memory).
