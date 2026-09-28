# Windows setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

The app runs with the default in-memory store and needs no Redis or API key.
Set `STORAGE_BACKEND=redis` (see `install_redis_windows.ps1`) for persistence.
