# Deploy the Industrial AI portal on Render

This deploy-ready version uses **one HTTP port**. It does not use `START_ALL.bat` on the server.

## Local test

```bash
python deploy_app.py
```

Open `http://127.0.0.1:10000`.

## Render

1. Put the contents of this folder in a GitHub repository.
2. Sign in to Render and choose **New > Web Service**.
3. Connect the GitHub repository.
4. Use:
   - Runtime: **Python**
   - Build command: `python --version`
   - Start command: `python deploy_app.py`
   - Plan: **Free** (for a demo)
5. Deploy.

Render supplies the `PORT` environment variable automatically. `deploy_app.py` binds to `0.0.0.0:$PORT`.

After deployment, use only the generated `https://<name>.onrender.com` URL. All layers are available inside the common portal.
