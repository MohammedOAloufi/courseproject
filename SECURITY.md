# Security Notes

## Secret Management
- All secrets are loaded from environment variables (see `.env.example`).
- Never commit `.env` files. The repository's `.gitignore` enforces this.
- For production (Render), set environment variables via the Render dashboard rather than uploading a `.env` file.

## Rotating Secrets (REQUIRED)
The following secrets were exposed in git history (commit `3308c89`) and **must** be rotated outside this repo:

1. **Cloudinary API Secret** — rotate from the Cloudinary dashboard → Settings → Security → API Keys.
2. **Database password** — rotate the Postgres user password from the Render dashboard.
3. **Django `SECRET_KEY`** — generate a new one:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(64))"
   ```
   and update the Render environment variable.

After rotation, scrub the history (optional but recommended):
```bash
pip install git-filter-repo
git filter-repo --path .env --invert-paths
git push --force --all
```

## Hardening Applied
- HSTS, SAMESITE, secure proxy header, referrer policy, frame deny.
- `django-axes` lockout on failed logins (5 attempts / 1 hour cooldown).
- Strict validation: production refuses to start with a missing/insecure `SECRET_KEY`.

## Verification Checklist
- [ ] `python manage.py check --deploy` shows zero warnings.
- [ ] `git ls-files .env` is empty.
- [ ] `curl -I` against the production URL shows `Strict-Transport-Security`, `X-Frame-Options: DENY`, `Referrer-Policy`.
- [ ] Five failed logins lock the account (django-axes).
- [ ] `python manage.py test` passes.
