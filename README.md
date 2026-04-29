# SmartBackup

A personal tool I built to back up files and folders to Telegram using a bot. It splits large files automatically, uploads them in chunks, and gives you a web UI to manage everything.

## What it does

- Splits files larger than 19MB into chunks and uploads them to Telegram
- Web interface to create backups, view history, restore, or delete
- Auto-Backup Folder on your Desktop — drop anything in it and it backs up automatically
- Tracks everything in a local SQLite database

## Setup

**Install dependencies**
```bash
pip install -r requirements.txt
```

**Set up the database**
```bash
python manage.py migrate
```

**Run the app**
```bash
python manage.py runserver
```

Then open http://localhost:8000 in your browser.

**Configure your Telegram bot**

The app will walk you through this on first launch. You'll need to create a bot via @BotFather on Telegram and get your Chat ID. Instructions are shown in the app.

## Auto-Backup Folder

A folder called `SmartBackupWatch` is created on your Desktop automatically. Anything you drop into it gets backed up to Telegram. The watcher starts automatically with the server.

If you want to run it manually in a separate terminal instead:
```bash
python manage.py start_watcher
```

## Project structure

smart-bakcup/
├── core/                   # Django project settings and URLs
├── backup_app/             # Main app — models, views, API
│   └── management/
│       └── commands/
│           └── start_watcher.py
├── templates/
│   └── index.html          # The entire frontend
├── config.py               # MAX_SIZE = 19MB, env loading
├── zipper.py
├── splitter.py
├── merger.py
├── telegram_uploader.py
├── telegram_downloader.py
└── requirements.txt

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/backup/ | Start a new backup |
| GET | /api/backups/ | List all backups |
| POST | /api/restore/\<id\>/ | Restore a backup |
| DELETE | /api/backups/\<id\>/ | Delete a backup record |
| GET | /api/config/ | Check if bot is configured |
| POST | /api/config/save/ | Save bot token and chat ID |
| POST | /api/config/test/ | Send a test message via the bot |

## Notes

- MAX_SIZE is intentionally 19MB. Telegram lets bots upload up to 50MB but the download API (getFile) caps at 20MB. Keeping chunks at 19MB makes both work reliably.
- The .env file stores your bot token and chat ID. Don't commit it.
- The watcher has a 3-second delay before triggering a backup so it doesn't fire mid-copy.

## Common issues

- **Invalid bot token** — copy it again from @BotFather, no extra spaces
- **Wrong Chat ID** — make sure you've sent at least one message to your bot before fetching the Chat ID
- **Upload failing** — check that your bot is the one you started a chat with, not a group or channel
